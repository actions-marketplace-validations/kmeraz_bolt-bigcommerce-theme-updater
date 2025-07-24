import shutil
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class BoltThemeModifier:
    def __init__(self, publishable_key: str, environment: str = "production", route_token: Optional[str] = None, openai_api_key: Optional[str] = None) -> None:
        self.publishable_key = publishable_key
        self.environment = environment
        self.route_token = route_token
        self.bolt_sandbox = environment == "sandbox"
        self.openai_client = OpenAI(api_key=openai_api_key)

    def read_theme_structure(self, theme_dir: Union[str, Path]) -> Dict[str, str]:
        """Read and analyze the entire theme structure"""
        theme_path = Path(theme_dir)
        theme_files: Dict[str, str] = {}

        # Common BigCommerce theme file extensions
        supported_extensions = ['.html', '.css', '.js', '.json', '.scss', '.handlebars', '.hbs']

        for file_path in theme_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                relative_path = file_path.relative_to(theme_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Truncate very large files to avoid token limits
                        if len(content) > 50000:
                            content = content[:50000] + "\\n... [truncated]"
                        theme_files[str(relative_path)] = content
                except Exception as e:
                    print(f"⚠️ Could not read {relative_path}: {e}")

        return theme_files

    def get_bolt_integration_prompt(self, theme_files: Dict[str, str]) -> str:
        """Create comprehensive prompt for OpenAI to analyze and modify the theme"""
        bolt_domain = "connectsandbox" if self.bolt_sandbox else "connect"

        # Build prompt components
        prompt_parts: List[str] = []
        prompt_parts.append("You are an expert BigCommerce theme developer tasked with integrating Bolt checkout functionality into a BigCommerce theme.")
        prompt_parts.append("")
        prompt_parts.append("INTEGRATION REQUIREMENTS:")
        prompt_parts.append(f"1. Add Bolt tracking script to the main layout/base template in the <head> section:")
        prompt_parts.append(f"   <script id='bolt-tracking' type='text/javascript' src='https://{bolt_domain}.bolt.com/track.js' data-publishable-key='{self.publishable_key}'></script>")
        prompt_parts.append("")
        prompt_parts.append(f"2. Add Bolt connect script to cart-related pages before closing </body> tag:")
        prompt_parts.append(f"   <script id='bolt-connect' src='https://{bolt_domain}.bolt.com/connect.js' data-auto-capture='true' data-auto-capture-elements='form[action*=checkout]' data-publishable-key='{self.publishable_key}'></script>")
        prompt_parts.append("")
        prompt_parts.append("3. Add Bolt checkout button to replace or supplement existing checkout buttons:")
        prompt_parts.append("   <div id='bolt-checkout-button'></div>")
        prompt_parts.append("   <script>")
        prompt_parts.append("   document.addEventListener('DOMContentLoaded', function() {")
        prompt_parts.append("     const originalButton = document.querySelector('.btn-checkout, .checkout-button, [href*=\"checkout\"]');")
        prompt_parts.append("     if (originalButton) { originalButton.style.display = 'none'; }")
        prompt_parts.append("     if (typeof BoltCheckout !== 'undefined') {")
        prompt_parts.append(f"       const boltCheckout = BoltCheckout.configure({{ publishableKey: '{self.publishable_key}', environment: '{self.environment}' }});")
        prompt_parts.append("       const checkoutButton = boltCheckout.create('checkout_button');")
        prompt_parts.append("       checkoutButton.mount('#bolt-checkout-button');")
        prompt_parts.append("     }")
        prompt_parts.append("   });")
        prompt_parts.append("   </script>")
        prompt_parts.append("")
        prompt_parts.append("THEME FILES STRUCTURE:")

        for file_path, content in theme_files.items():
            prompt_parts.append(f"--- FILE: {file_path} ---")
            prompt_parts.append(content)
            prompt_parts.append("")

        prompt_parts.append("INSTRUCTIONS:")
        prompt_parts.append("1. Analyze the theme structure and identify the appropriate files to modify")
        prompt_parts.append("2. Determine the best locations for each Bolt integration component based on the theme's architecture")
        prompt_parts.append("3. Integrate Bolt functionality while preserving existing theme functionality")
        prompt_parts.append("4. Return ONLY the files that need modifications with their complete updated content")
        prompt_parts.append("5. Use proper BigCommerce templating syntax (Handlebars/Stencil)")
        prompt_parts.append("6. Ensure the integration is compatible with the existing theme structure")
        prompt_parts.append("")
        prompt_parts.append("RESPONSE FORMAT:")
        prompt_parts.append("For each file that needs modification, provide:")
        prompt_parts.append("FILE_PATH: path/to/file.html")
        prompt_parts.append("CONTENT:")
        prompt_parts.append("[complete file content with Bolt integration]")
        prompt_parts.append("")
        prompt_parts.append("Only include files that require changes. Do not include unchanged files.")

        return "\\n".join(prompt_parts)

    def get_openai_modifications(self, theme_files: Dict[str, str]) -> Optional[str]:
        """Use OpenAI to analyze theme and provide modifications"""
        if not self.openai_client:
            print("⚠️ No OpenAI API key provided, skipping AI analysis")
            return None

        prompt = self.get_bolt_integration_prompt(theme_files)

        print("🤖 Analyzing theme structure with OpenAI...")
        print(f"📊 Sending {len(theme_files)} files for analysis...")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=16000,
                temperature=0.1
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return None

    def parse_openai_response(self, response_content: str) -> Dict[str, str]:
        """Parse OpenAI response to extract file modifications"""
        modifications: Dict[str, str] = {}

        print("📝 Parsing OpenAI response...")
        print(f"Response length: {len(response_content)} characters")

        # Split response into sections
        sections = response_content.split('FILE_PATH:')

        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split('\\n')
            if not lines:
                continue

            # Extract file path
            file_path = lines[0].strip()
            print(f"🔄 Processing file: {file_path}")

            # Find content section
            content_start = -1
            for i, line in enumerate(lines):
                if line.strip().lower().startswith('content:'):
                    content_start = i + 1
                    break

            if content_start > 0:
                file_content = '\\n'.join(lines[content_start:])
                modifications[file_path] = file_content
                print(f"✅ Captured {len(file_content)} characters for {file_path}")
            else:
                print(f"⚠️ Could not find content section for {file_path}")

        print(f"📊 Total files to modify: {len(modifications)}")
        return modifications

    def process_theme_directory(self, theme_dir: Optional[Union[str, Path]], output_dir: Optional[Union[str, Path]]) -> List[str]:
        """Process entire theme directory using OpenAI"""
        if theme_dir is None or output_dir is None:
            raise ValueError("theme_dir and output_dir must be provided")

        theme_path = Path(theme_dir)
        output_path = Path(output_dir)

        if not theme_path.exists():
            print(f"⚠️ Theme directory does not exist: {theme_dir}")
            print("📁 Creating minimal theme structure for testing...")
            self.create_minimal_theme_structure(theme_path)

        # Copy entire theme to output directory
        if output_path.exists():
            shutil.rmtree(output_path)
        shutil.copytree(theme_path, output_path)

        print("📁 Reading theme structure...")
        theme_files = self.read_theme_structure(theme_dir)
        print(f"📊 Found {len(theme_files)} theme files to analyze")

        # Show file list
        for file_path in theme_files.keys():
            print(f"  - {file_path}")

        # Get OpenAI modifications
        openai_response = self.get_openai_modifications(theme_files)
        if not openai_response:
            print("❌ Failed to get OpenAI modifications")
            return []

        # Parse OpenAI response
        modifications_dict = self.parse_openai_response(openai_response)

        if not modifications_dict:
            print("⚠️ No modifications found in OpenAI response")
            # Save raw response for debugging
            with open("openai_response_debug.txt", "w") as f:
                f.write(openai_response)
            print("⚠️ Raw OpenAI response saved to openai_response_debug.txt")
            return []

        applied_modifications: List[str] = []

        # Apply modifications
        for file_path, modified_content in modifications_dict.items():
            full_path = output_path / file_path

            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"📝 Applying AI modifications to {file_path}...")

            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)

                applied_modifications.append(file_path)
                print(f"✅ Modified {file_path}")

            except Exception as e:
                print(f"❌ Error modifying {file_path}: {e}")

        return applied_modifications

    def create_minimal_theme_structure(self, theme_path: Path) -> None:
        """Create minimal theme structure for testing"""
        theme_path.mkdir(parents=True, exist_ok=True)

        # Create basic directory structure
        (theme_path / "templates" / "layout").mkdir(parents=True, exist_ok=True)
        (theme_path / "templates" / "pages").mkdir(parents=True, exist_ok=True)
        (theme_path / "templates" / "components" / "cart").mkdir(parents=True, exist_ok=True)
        (theme_path / "assets" / "css").mkdir(parents=True, exist_ok=True)
        (theme_path / "assets" / "js").mkdir(parents=True, exist_ok=True)

        # Create basic base.html
        base_html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <meta charset='utf-8'>",
            "    <title>{{page.title}}</title>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1'>",
            "</head>",
            "<body>",
            "    <header>",
            "        <h1>{{store.name}}</h1>",
            "    </header>",
            "    <main>",
            "        {{content}}",
            "    </main>",
            "    <footer>",
            "        <p>&copy; {{store.name}}</p>",
            "    </footer>",
            "</body>",
            "</html>"
        ]
        base_html = "\\n".join(base_html_lines)

        with open(theme_path / "templates" / "layout" / "base.html", "w") as f:
            f.write(base_html)

        # Create basic cart.html
        cart_html_lines = [
            "<div class='cart-page'>",
            "    <h2>Shopping Cart</h2>",
            "    <div class='cart-items'>",
            "        {{#each cart.items}}",
            "        <div class='cart-item'>",
            "            <h3>{{name}}</h3>",
            "            <p>Price: {{price}}</p>",
            "            <p>Quantity: {{quantity}}</p>",
            "        </div>",
            "        {{/each}}",
            "    </div>",
            "    <div class='cart-total'>",
            "        <p>Total: {{cart.total}}</p>",
            "    </div>",
            "    <div class='checkout-section'>",
            "        <button class='btn-checkout'>Checkout</button>",
            "    </div>",
            "</div>"
        ]
        cart_html = "\\n".join(cart_html_lines)

        with open(theme_path / "templates" / "pages" / "cart.html", "w") as f:
            f.write(cart_html)

        # Create basic cart preview
        cart_preview_html_lines = [
            "<div class='cart-preview'>",
            "    <h3>Cart Preview</h3>",
            "    <div class='cart-items-preview'>",
            "        {{#each cart.items}}",
            "        <div class='cart-item-preview'>",
            "            <span>{{name}}</span>",
            "            <span>{{price}}</span>",
            "        </div>",
            "        {{/each}}",
            "    </div>",
            "    <div class='cart-actions'>",
            "        <a href='/cart' class='view-cart'>View Cart</a>",
            "        <a href='/checkout' class='checkout-button'>Checkout</a>",
            "    </div>",
            "</div>"
        ]
        cart_preview_html = "\\n".join(cart_preview_html_lines)

        with open(theme_path / "templates" / "components" / "cart" / "preview.html", "w") as f:
            f.write(cart_preview_html)

        print("✅ Created minimal theme structure for testing")

def main() -> None:
    # Get inputs from environment
    theme_dir = sys.argv[1]
    output_dir = sys.argv[2]
    publishable_key = sys.argv[3]
    environment = sys.argv[4]
    theme_name = sys.argv[5]
    route_token = sys.argv[6]
    openai_api_key = sys.argv[7]

    print(f"🚀 Starting Bolt BigCommerce theme integration...")
    print(f"📁 Theme directory: {theme_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🔑 Environment: {environment}")

    # Validate required inputs
    if not publishable_key or publishable_key.strip() == "":
        print("❌ Error: publishable_key is required but not provided")
        sys.exit(1)

    if not openai_api_key or openai_api_key.strip() == "":
        print("❌ Error: openai_api_key is required but not provided")
        sys.exit(1)

    # Initialize theme modifier
    modifier = BoltThemeModifier(
        publishable_key=publishable_key,
        environment=environment or "production",
        route_token=route_token,
        openai_api_key=openai_api_key
    )

    try:
        # Process the theme directory
        modifications = modifier.process_theme_directory(theme_dir, output_dir)

        print(f"✅ Successfully modified {len(modifications)} files:")
        for mod in modifications:
            print(f"  - {mod}")

        # Create summary
        summary: Dict[str, Any] = {
            "success": True,
            "theme_name": theme_name,
            "environment": environment,
            "modifications": modifications,
            "output_directory": output_dir
        }

        with open("bolt_integration_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        print(f"📋 Integration summary saved to bolt_integration_summary.json")
        print(f"🎉 Bolt integration completed successfully!")

    except Exception as e:
        print(f"❌ Error during integration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
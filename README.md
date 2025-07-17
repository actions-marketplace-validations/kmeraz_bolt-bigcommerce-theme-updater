# BigCommerce Theme Updater for Bolt

A GitHub Action that automatically integrates Bolt checkout functionality into BigCommerce themes using AI-powered analysis and modification.

## Features

- **AI-Powered Integration**: Uses OpenAI GPT-4o to analyze theme structure and intelligently add Bolt checkout components
- **Automatic Theme Analysis**: Scans theme files to understand structure and identify optimal integration points
- **Smart Modifications**: Adds Bolt tracking scripts, connect scripts, and checkout buttons in appropriate locations
- **Complete Artifact Generation**: Creates modified theme ZIP and detailed installation guide
- **Local Testing Support**: Full compatibility with `act` tool for local development workflow
- **Environment-Aware**: Supports both sandbox and production Bolt environments

## Inputs

| Name               | Description                                 | Required | Default               |
| ------------------ | ------------------------------------------- | -------- | --------------------- |
| `theme_directory`  | Path to the BigCommerce theme directory     | Yes      | -                     |
| `output_directory` | Path where modified theme will be saved     | Yes      | -                     |
| `publishable_key`  | Bolt publishable key                        | Yes      | -                     |
| `environment`      | Bolt environment (sandbox/production)       | No       | `sandbox`             |
| `theme_name`       | Name for the modified theme                 | No       | `Bolt-Modified-Theme` |
| `openai_api_key`   | OpenAI API key for AI-powered modifications | No       | -                     |

## Outputs

| Name                      | Description                         |
| ------------------------- | ----------------------------------- |
| `theme_zip_path`          | Path to the modified theme ZIP file |
| `installation_guide_path` | Path to the installation guide      |

## Usage

### Basic Usage

```yaml
name: Integrate Bolt Checkout
on: [push]

jobs:
  integrate-bolt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Integrate Bolt into Theme
        uses: ./
        with:
          theme_directory: './my-theme'
          output_directory: './bolt-modified-theme'
          publishable_key: ${{ secrets.BOLT_PUBLISHABLE_KEY }}
          environment: 'production'
          theme_name: 'My-Store-Bolt-Theme'
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Advanced Usage with Multiple Themes

```yaml
name: Multi-Theme Bolt Integration
on: [push]

jobs:
  integrate-bolt:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        theme: [cornerstone, stencil-utils, custom-theme]
    steps:
      - uses: actions/checkout@v3

      - name: Integrate Bolt into ${{ matrix.theme }}
        uses: ./
        with:
          theme_directory: './themes/${{ matrix.theme }}'
          output_directory: './output/${{ matrix.theme }}-bolt'
          publishable_key: ${{ secrets.BOLT_PUBLISHABLE_KEY }}
          environment: 'production'
          theme_name: '${{ matrix.theme }}-Bolt-Enhanced'
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload Theme Artifact
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.theme }}-bolt-theme
          path: ./output/${{ matrix.theme }}-bolt-theme.zip
```

## Local Testing

This action supports local testing using the `act` tool, which allows you to run GitHub Actions locally.

### Prerequisites

1. Install [act](https://github.com/nektos/act):
   ```bash
   brew install act
   ```

2. Ensure Docker is running

### Setup

1. Create a `.env` file in the action directory:
   ```env
   INPUT_THEME_DIRECTORY=./my-theme
   INPUT_OUTPUT_DIRECTORY=./test-output
   INPUT_PUBLISHABLE_KEY=pk_test_your_bolt_key
   INPUT_ENVIRONMENT=sandbox
   INPUT_THEME_NAME=My-Local-Test-Theme
   INPUT_OPENAI_API_KEY=sk-your_openai_api_key
   ```

2. Run the test script:
   ```bash
   ./test-local.sh
   ```

   Or run act directly:
   ```bash
   act --env-file .env
   ```

### Local Testing Features

- **No Artifact Upload**: Skips GitHub artifact upload in local environment
- **Local File Output**: Creates theme ZIP and installation guide locally
- **Console Summary**: Displays integration results in terminal
- **Debug Output**: Shows detailed processing information

## AI-Powered Modifications

When an OpenAI API key is provided, the action performs intelligent theme analysis:

### Analysis Process

1. **Theme Structure Scan**: Analyzes all template files, components, and layouts
2. **Content Analysis**: Reads file contents to understand theme architecture
3. **Integration Planning**: Uses AI to determine optimal placement for Bolt components
4. **Code Generation**: Creates theme-specific integration code

### Modification Types

- **Tracking Scripts**: Adds Bolt analytics and tracking to theme head
- **Connect Scripts**: Integrates Bolt connection functionality
- **Checkout Buttons**: Replaces or enhances existing checkout buttons
- **Cart Integration**: Modifies cart templates for Bolt compatibility
- **Layout Updates**: Updates base layouts for consistent Bolt integration

### Fallback Behavior

If no OpenAI API key is provided:
- Creates minimal theme structure for testing
- Performs basic static modifications
- Generates installation guide with manual steps

## Generated Artifacts

### Modified Theme ZIP

- Complete theme with Bolt integration
- Maintains original theme structure
- Includes all necessary Bolt components
- Ready for upload to BigCommerce

### Installation Guide

Comprehensive guide including:
- Step-by-step installation instructions
- Configuration requirements
- Testing procedures
- Troubleshooting tips

### Integration Summary

JSON summary containing:
- List of modified files
- Integration success status
- Theme metadata
- Environment configuration

## Environment Support

### Sandbox Environment
- Uses Bolt sandbox API endpoints
- Test publishable keys (pk_test_*)
- Safe for development and testing

### Production Environment
- Uses Bolt production API endpoints
- Live publishable keys (pk_prod_*)
- For live store deployment

## Error Handling

The action includes comprehensive error handling:

- **Missing Theme Directory**: Creates minimal structure for testing
- **Invalid API Keys**: Graceful degradation with manual instructions
- **Network Issues**: Retries with exponential backoff
- **File System Errors**: Detailed error reporting and cleanup

## Security Considerations

- Never commit API keys to version control
- Use GitHub Secrets for sensitive values
- Validate all inputs before processing
- Sanitize file paths and names

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `act`
5. Submit a pull request

## Support

For issues and questions:
- Create an issue in this repository
- Review existing issues for solutions
- Check the troubleshooting section in generated guides

## License

MIT License - see LICENSE file for details

# LLM Theme Updater for Bolt + BigCommerce

This GitHub Action updates your BigCommerce theme to include **Bolt Checkout** by automatically modifying your theme files according to [Step 6: Add Scripts & Buttons](https://help.bolt.com/platforms/bigcommerce/bigcommerce-setup-guide/bigcommerce-installation/#step-6-add-scripts--buttons) in Bolt's setup guide.

---

## 🚀 What It Does

- Automatically updates a specified theme file (e.g. `templates/layout/base.html`) using OpenAI GPT-4.
- Injects Bolt's required `<script>` tags and button markup.
- Pushes changes to a new branch so you can review them before merging.

---

## 📦 Inputs

| Name             | Required | Description                                                                   |
| ---------------- | -------- | ----------------------------------------------------------------------------- |
| `file_path`      | ✅        | Path to the theme file you want to update (e.g. `templates/layout/base.html`) |
| `openai_api_key` | ✅        | Your OpenAI API key stored as a GitHub secret                                 |

---

## 🛠 Example Usage

```yaml
name: Update BigCommerce Theme with Bolt

on:
  workflow_dispatch:
    inputs:
      file_path:
        description: 'Path to the theme file to update'
        required: true

jobs:
  bolt-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: bolt/bigcommerce-theme-updater@v1
        with:
          file_path: ${{ github.event.inputs.file_path }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}

      - name: Commit and Push
        run: |
          git config user.name "bolt-bot"
          git config user.email "bot@bolt.com"
          git checkout -b bolt-bigcommerce-theme-updater
          git add ${{ github.event.inputs.file_path }}
          git commit -m "Add Bolt scripts and buttons"
          git push origin bolt-bigcommerce-theme-updater

      - uses: peter-evans/create-pull-request@v5
        with:
          title: "Add Bolt Checkout Integration"
          body: "This PR adds the required scripts and buttons to support Bolt Checkout."
          head: bolt-bigcommerce-theme-updater
          base: main


# Selenium Automation – BrowserStack Technical Assignment

This project demonstrates web scraping, API integration, text processing, and cross-browser execution using Selenium.

---

## ✅ Assignment Coverage

- Visit El País Opinion section (Spanish website)
- Scrape first 5 articles
- Print article titles and content in Spanish
- Download cover images (if available)
- Translate titles to English using a Translation API
- Identify words repeated more than twice across translated titles
- Run locally
- Execute on BrowserStack across 3 parallel sessions (desktop + mobile)

---

## 📂 Project Structure

```
project-root/
│
├── test/
│   ├── local-test.py      # Local execution
│   └── test2.py           # BrowserStack multi-platform execution
│
├── browserstack.yml
├── requirements.txt
└── README.md
```

Images are saved in dynamically generated folders to ensure parallel-safe execution.

---

## ▶ Run Locally

```
python test/local-test.py
```

---

## ☁ Run on BrowserStack

```
browserstack-sdk python test/test2.py
```

---

## ☁ Run on BrowserStack

- View the public build in browserstack automation for parallel testng on multiple browsers.
- https://automate.browserstack.com/projects/BrowserStack+Sample/builds/browserstack-build/18?public_token=12aa6e64bb9ef9205401aa08561a63a2ce2ed98e7878e2be836537a0f38afe35

---

This implementation demonstrates Selenium automation, API integration, parallel execution, and proper BrowserStack session handling.


import os
from pathlib import Path
import json

import requests
from robocorp import browser
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel

FILE_NAME = "challenge.xlsx"
EXCEL_URL = f"https://rpachallenge.com/assets/downloadFiles/{FILE_NAME}"
OUTPUT_DIR = Path(os.getenv("ROBOT_ARTIFACTS", "output"))


@task
def solve_challenge():
    """
    Main task which solves the RPA challenge!

    Downloads the source data Excel file and uses Playwright to fill the entries inside
    rpachallenge.com.
    """
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=True,
    )
    try:
        # Reads a table from an Excel file hosted online.
        excel_file = download_file(
            EXCEL_URL, target_dir=OUTPUT_DIR, target_filename=FILE_NAME
        )
        excel = Excel()
        excel.open_workbook(str(excel_file))
        rows = excel.read_worksheet_as_table("Sheet1", header=True)

        # Convert Table to a list of dictionaries for JSON serialization
        list_of_rows = [dict(row) for row in rows]

        # Surf the automation challenge website and fill in information from the table
        #  extracted above.
        page = browser.goto("https://rpachallenge.com/")
        page.click("button:text('Start')")
        fill_all_forms_at_once(list_of_rows, page=page)
        element = page.locator("css=div.congratulations")
        browser.screenshot(element)
    finally:
        # A place for teardown and cleanups. (Playwright handles browser closing)
        print("Automation finished!")


def download_file(url: str, *, target_dir: Path, target_filename: str) -> Path:
    """
    Downloads a file from the given URL into a custom folder & name.

    Args:
        url: The target URL from which we'll download the file.
        target_dir: The destination directory in which we'll place the file.
        target_filename: The local file name inside which the content gets saved.

    Returns:
        Path: A Path object pointing to the downloaded file.
    """
    # Obtain the content of the file hosted online.
    response = requests.get(url)
    response.raise_for_status()  # this will raise an exception if the request fails
    # Write the content of the request response to the target file.
    target_dir.mkdir(exist_ok=True)
    local_file = target_dir / target_filename
    local_file.write_bytes(response.content)
    return local_file


def fill_all_forms_at_once(rows: list, *, page: browser.Page):
    """
    Fills and submits all forms using a single JavaScript injection for max speed.
    """
    # Convert all row data to a JSON string to be injected into the browser
    all_rows_json = json.dumps(rows)

    js_code = f"""
    const fieldMap = {{
        "First Name": "labelFirstName",
        "Last Name": "labelLastName",
        "Company Name": "labelCompanyName",
        "Role in Company": "labelRole",
        "Address": "labelAddress",
        "Email": "labelEmail",
        "Phone Number": "labelPhone",
    }};
    const allRows = {all_rows_json};

    for (const row of allRows) {{
        for (const [key, ngName] of Object.entries(fieldMap)) {{
            const el = document.querySelector(`input[ng-reflect-name='${{ngName}}']`);
            if (el) {{
                el.value = row[key] || '';
            }}
        }}
        document.querySelector("input[type='submit']").click();
    }}
    """
    page.evaluate(js_code)
    return []

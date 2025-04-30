import asyncio
import argparse
import os
import subprocess
from playwright.async_api import async_playwright

async def get_command_output(query: str, query_type: str, package_manager: str = None):
    base_url = "https://osfm-ata.vercel.app/"
    url = f"{base_url}?q={query.replace(' ', '%20')}&t={query_type}"
    if query_type == "pm" and package_manager:
        url += f"&pm={package_manager}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("pre.command-code.text-white", timeout=5000)
        content = await page.text_content("pre.command-code.text-white")
        await browser.close()
        return content.strip() if content else "Command not found or failed to load."

def parse_args():
    parser = argparse.ArgumentParser(description="Fetch terminal commands from osfm-ata.vercel.app")
    parser.add_argument("query", help="Your query, e.g. 'install python'")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ps", action="store_true", help="Use PowerShell output")
    group.add_argument("--b", action="store_true", help="Use Bash output")
    group.add_argument("--apt", action="store_true", help="Use apt package manager")
    group.add_argument("--dnf", action="store_true", help="Use dnf package manager")
    group.add_argument("--pacman", action="store_true", help="Use pacman package manager")

    return parser.parse_args()

if __name__ == "__main__":
    subprocess.run("pip install playwright",shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.run("playwright install",shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    args = parse_args()

    # Determine type and package manager
    if args.ps:
        query_type = "ps"
        pm = None
    elif args.b:
        query_type = "b"
        pm = None
    elif args.apt:
        query_type = "pm"
        pm = "apt"
    elif args.dnf:
        query_type = "pm"
        pm = "dnf"
    elif args.pacman:
        query_type = "pm"
        pm = "pacman"
    else:
        raise ValueError("No valid query type flag provided.")

    output = asyncio.run(get_command_output(args.query, query_type, pm))
    print("\nCommand Output:\n")
    print(output)

# darkweb-search-R
Tor-powered dark web search aggregator that supports multiple engines, async scraping, SQLite/CSV storage, and custom engine configs.

**✨ Features**  
🔎 Search multiple .onion engines at once  
⚡ Async (fast) queries using aiohttp  
💾 Save results to SQLite or CSV in a /results folder  
🧩 Easily add new engines by editing search_engines.json  
🎯 Select specific engines with --engines  

**🚀 Installation**  
Clone this repo:  
git clone https://github.com/hadleys-hope-lv426/darkweb-search-R.git  
cd darkweb-search-R  

Create a virtual environment and install requirements:  
python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  

Make sure Tor is running locally (default SOCKS proxy: 127.0.0.1:9050):  
tor

**⚡ Usage**  
Search all engines (default saves to SQLite):  
python3 darkweb-search-R.py "cats"  

Search and save results to CSV:  
python3 darkweb-search-R.py "cats" --output csv  

Search with specific engines:  
python3 darkweb-search-R.py "cats" --engines ahmia onionland  

**🔧 Adding New Engines**  
I will aim to add more search engines shortly. But you can add your own darkweb search engines by editing the "search_engines.json" file and adding darkweb search sites using the format below:  

"ahmia": {  
  "url": "http://ahmiafi3n2nldsy.onion/search/?q={query}",  
  "selector": "li.result h4 a",  
  "attr": "href"  
}

* url: the search URL with {query} as a placeholder  
* selector: CSS selector to extract links  
* attr: usually "href" to capture the link  

**⚠️ Disclaimer**  
This tool is for educational and OSINT research purposes only.  
The author does not endorse or condone illegal activity. You are responsible for how you use this software.  

**📜 License**  
Released under the MIT License


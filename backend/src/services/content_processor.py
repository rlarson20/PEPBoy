"""
use existing get_raw_pep_text()
use docutils to turn RST to HTML
sanitize
handle PEP-specific RST directives (figure out what this is)
produce HTML fit for react site
"""

"""
need to add content field to PEP model (needed for FTS)
store processed HTML in database field
implement lazy loading for large files
"""
"""
add `/api/peps/{num}/content` endpoint for raw html
add content field for existing PEP detail endpoint
"""
from docutils.core import publish_string
from bs4 import BeautifulSoup
from .data_fetcher import get_raw_pep_text


def process_pep_content(filename: str) -> str:
    """Make clean HTML"""
    rst = get_raw_pep_text(filename)
    html = publish_string(rst, writer_name="html5")
    soup = BeautifulSoup(
        html, "html.parser"
    )  # may change to lxml parser for speed later
    return str(soup)


"""succeeds when pep is rendered as clean html, general formatting is preserved (because want to make it my own) and content api endpoint exists and works"""

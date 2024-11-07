doc_links = {
    "dirty_repo": "https://docs.getdocsy.com/docsy-cli/apply",
}

class DocsyCLIError(Exception):
    """CLI-specific error that includes a documentation URL."""
    
    def __init__(self, message: str, doc_url: str):
        self.doc_url = doc_links[doc_url]
        super().__init__(f"{message}\n visit: {self.doc_url}")


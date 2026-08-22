import pytest
from src.structure import build_3dmol_html

def test_build_3dmol_html_escaping():
    malicious_pdb = "ATOM   1  N   ALA A   1      0.000   0.000   0.000\n</script><script>alert('XSS')</script>`'"
    html_output = build_3dmol_html(malicious_pdb)
    
    # Template asli punya tepat 2 tag penutup </script>
    assert html_output.count("</script>") == 2

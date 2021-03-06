from ptah import rst
from ptah.testing import TestCase


class TestRST(TestCase):

    def tearDown(self):
        rst.local_data.sphinx = None

    def test_rst_py_domain(self):
        text = """ Test text :py:class:`ptahcms.Node` """

        self.assertIn('Test text '
                      '<code class="xref py py-class docutils literal">'
                      '<span class="pre">ptahcms.Node</span></code>',
                      rst.rst_to_html(text))

    def test_rst_error(self):
        text = """ Test text `ptahcms.Node` """

        self.assertEqual(
            '<pre> Test text `ptahcms.Node` </pre>', rst.rst_to_html(text))

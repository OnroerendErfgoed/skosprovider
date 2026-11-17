from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language


class TestExtractLanguage:

    def test_extract_language_nlBE(self):
        assert "nl-BE" == extract_language("nl-BE")

    def test_extract_language_None(self):
        assert "und" == extract_language(None)


class TestHtml:

    def test_lang_und(self):
        assert "" == add_lang_to_html("", "und")
        assert "<p></p>" == add_lang_to_html("<p></p>", "und")

    def test_lang_no_html(self):
        assert '<div xml:lang="en"></div>' == add_lang_to_html("", "en")

    def test_no_single_child(self):
        html = "<p>Paragraph 1</p><p>Paragraph2</p>"
        assert (
            '<div xml:lang="en"><p>Paragraph 1</p><p>Paragraph2</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_text_node(self):
        html = "Something"
        assert '<div xml:lang="en">Something</div>' == add_lang_to_html(html, "en")

    def test_single_child_no_attributes(self):
        html = "<p>Paragraph 1</p>"
        assert '<div xml:lang="en"><p>Paragraph 1</p></div>' == add_lang_to_html(
            html, "en"
        )

    def test_single_child_already_has_langs(self):
        html = '<p xml:lang="en">Paragraph 1</p>'
        assert (
            '<div xml:lang="en"><p xml:lang="en">Paragraph 1</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_single_child_other_attributes(self):
        html = '<p class="something">Paragraph 1</p>'
        assert (
            '<div xml:lang="en"><p class="something">Paragraph 1</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_lang_und_preserves_html(self):
        html = "<p>Paragraph 1</p><p>Paragraph 2</p>"
        assert html == add_lang_to_html(html, "und")

    def test_nested_single_element(self):
        html = "<div><p>Paragraph</p></div>"
        assert '<div xml:lang="en"><p>Paragraph</p></div>' == add_lang_to_html(
            html, "en"
        )

    def test_already_wrapped_xml_lang_is_replaced(self):
        html = '<div xml:lang="fr"><p>Paragraph</p></div>'
        assert '<div xml:lang="en"><p>Paragraph</p></div>' == add_lang_to_html(
            html, "en"
        )

    def test_existing_div_attrs_preserved(self):
        html = '<div class="note"><p>Paragraph</p></div>'
        assert (
            '<div xml:lang="en" class="note"><p>Paragraph</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_idempotent_on_repeated_calls(self):
        html = "<p>Paragraph</p>"
        once = add_lang_to_html(html, "en")
        assert once == add_lang_to_html(once, "en")

    def test_multiple_divs_not_single_root(self):
        html = "<div>a</div><div>b</div>"
        assert '<div xml:lang="en"><div>a</div><div>b</div></div>' == add_lang_to_html(
            html, "en"
        )

    def test_inner_div_alongside_other_content(self):
        html = "<div>a</div><p>b</p>"
        assert '<div xml:lang="en"><div>a</div><p>b</p></div>' == add_lang_to_html(
            html, "en"
        )

    def test_nested_div_inside_single_root(self):
        html = "<div>outer<div>inner</div></div>"
        assert '<div xml:lang="en">outer<div>inner</div></div>' == add_lang_to_html(
            html, "en"
        )

    def test_text_before_element(self):
        html = "before<p>p</p>"
        assert '<div xml:lang="en">before<p>p</p></div>' == add_lang_to_html(html, "en")

    def test_text_after_element(self):
        html = "<p>p</p>after"
        assert '<div xml:lang="en"><p>p</p>after</div>' == add_lang_to_html(html, "en")

    def test_single_element_existing_inner_lang_preserved(self):
        html = '<p xml:lang="de">Paragraph</p>'
        assert (
            '<div xml:lang="en"><p xml:lang="de">Paragraph</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_multiple_elements_each_with_lang(self):
        html = '<p xml:lang="de">a</p><p xml:lang="fr">b</p>'
        assert (
            '<div xml:lang="en"><p xml:lang="de">a</p><p xml:lang="fr">b</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_self_closing_element(self):
        html = "<br/>"
        assert '<div xml:lang="en"><br/></div>' == add_lang_to_html(html, "en")

    def test_html_entities_preserved(self):
        html = "<p>A &amp; B</p>"
        assert '<div xml:lang="en"><p>A &amp; B</p></div>' == add_lang_to_html(
            html, "en"
        )

    def test_whitespace_only_input(self):
        assert '<div xml:lang="en">   </div>' == add_lang_to_html("   ", "en")

    def test_region_subtag_lang(self):
        html = "<p>hello</p>"
        assert '<div xml:lang="nl-BE"><p>hello</p></div>' == add_lang_to_html(
            html, "nl-BE"
        )

    def test_leading_comment_forces_wrap(self):
        html = "<!-- comment --><p>x</p>"
        assert '<div xml:lang="en"><!-- comment --><p>x</p></div>' == add_lang_to_html(
            html, "en"
        )

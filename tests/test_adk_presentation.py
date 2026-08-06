from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AdkPresentationContractTests(unittest.TestCase):
    def test_html_loads_product_presentation_layer(self):
        html = (ROOT / "web" / "adk.html").read_text(encoding="utf-8")
        self.assertIn('/assets/adk-product.css', html)
        self.assertIn('Cápsulas de trabajo', html)
        self.assertIn('Candidatos comparables', html)
        self.assertIn('Final KIRA', html)
        self.assertIn('Razonamiento privado', html)

    def test_javascript_renders_markdown_and_collapses_raw_payloads(self):
        javascript = (ROOT / "web" / "adk.js").read_text(encoding="utf-8")
        self.assertIn('function renderMarkdown', javascript)
        self.assertIn('className = "raw-details"', javascript)
        self.assertIn('Ver entrega completa', javascript)
        self.assertIn('Razonamiento privado protegido', javascript)
        self.assertNotIn('refs.finalText.textContent = record.texts', javascript)

    def test_candidate_board_is_created_from_atlas_output(self):
        javascript = (ROOT / "web" / "adk.js").read_text(encoding="utf-8")
        for marker in (
            'function extractCandidateCards',
            'CANDIDATOS GENERADOS AUTÓNOMAMENTE',
            'function renderCandidateBoard',
            'candidate_architecture',
            'Regla de Rechazo',
            'Ruta de Fabricación Local',
        ):
            self.assertIn(marker, javascript)

    def test_only_kira_can_fill_the_terminal_decision_card(self):
        javascript = (ROOT / "web" / "adk.js").read_text(encoding="utf-8")
        self.assertIn('agentName === "kira"', javascript)
        self.assertIn('const isKiraTerminal', javascript)
        self.assertIn('refs.finalText.replaceChildren(renderMarkdown', javascript)
        self.assertIn('Misión completada con decisión final de KIRA', javascript)

    def test_research_results_are_presented_as_cards(self):
        javascript = (ROOT / "web" / "adk.js").read_text(encoding="utf-8")
        for marker in (
            'function renderResearchBoard',
            'BÚSQUEDA EXTERNA COMPLETADA',
            'research-card',
            'Abrir fuente ↗',
        ):
            self.assertIn(marker, javascript)

    def test_styles_cover_capsules_markdown_candidates_and_research(self):
        css = (ROOT / "web" / "adk-product.css").read_text(encoding="utf-8")
        for marker in (
            '.agent-capsule',
            '.capsule-activity',
            '.markdown-body',
            '.candidate-board',
            '.candidate-card',
            '.research-board',
            '.research-card',
        ):
            self.assertIn(marker, css)


if __name__ == "__main__":
    unittest.main()

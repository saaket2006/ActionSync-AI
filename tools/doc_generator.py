import os
import logging
from typing import Dict, Any
import fitz  # PyMuPDF
from tools.registry import BaseActionSyncTool, tool_registry
from config.settings import settings

logger = logging.getLogger("actionsync.tools.doc_generator")

class DocumentGenerator(BaseActionSyncTool):
    def __init__(self):
        super().__init__(
            name="DocumentGenerator",
            description="Generates executive meeting reports in Markdown and PDF formats."
        )

    def initialize(self) -> None:
        os.makedirs(settings.GENERATED_DOCS_DIR, exist_ok=True)
        self.initialized = True

    def execute(self, meeting_title: str, pipeline_output: Dict[str, Any]) -> Dict[str, str]:
        """Generates MD and PDF reports.
        
        Returns:
            Dict containing:
            - markdown_path: Path to the generated Markdown report
            - pdf_path: Path to the generated PDF report
        """
        safe_title = "".join([c if c.isalnum() else "_" for c in meeting_title])
        timestamp = "".join([c if c.isdigit() else "" for c in str(fitz.get_tiss())])[:10] if hasattr(fitz, "get_tiss") else "report"
        
        md_filename = f"{safe_title}_{timestamp}.md"
        pdf_filename = f"{safe_title}_{timestamp}.pdf"
        
        md_path = os.path.join(settings.GENERATED_DOCS_DIR, md_filename)
        pdf_path = os.path.join(settings.GENERATED_DOCS_DIR, pdf_filename)
        
        # 1. Generate Markdown content
        md_content = self._build_markdown_content(meeting_title, pipeline_output)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        # 2. Generate PDF using PyMuPDF
        self._build_pdf_report(pdf_path, meeting_title, pipeline_output)
        
        logger.info(f"Generated documents: MD={md_path}, PDF={pdf_path}")
        return {
            "markdown_path": md_path,
            "pdf_path": pdf_path
        }

    def validate(self, output: Any) -> bool:
        if not isinstance(output, dict):
            return False
        return "markdown_path" in output and "pdf_path" in output

    def _build_markdown_content(self, title: str, data: Dict[str, Any]) -> str:
        sum_data = data.get("summarizer", {})
        dec_data = data.get("decision", {})
        task_data = data.get("action_item", {})
        risk_data = data.get("risk", {})
        timeline_data = data.get("timeline", {})
        impact_data = data.get("community_impact", {})
        acc_data = data.get("accountability", {})
        clar_data = data.get("clarification", {})

        md = f"# ActionSync AI - Meeting Intelligence Report\n"
        md += f"## Title: {title}\n"
        md += f"**Generated At:** {os.environ.get('CURRENT_TIME', '2026-06-29')}\n\n"
        md += f"---\n\n"
        
        # Executive Summary
        md += f"### 1. Executive Summary\n"
        md += f"{sum_data.get('executive_summary', 'No summary available.')}\n\n"
        md += f"**Key Topics:** {', '.join(sum_data.get('key_topics', []))}\n\n"
        md += f"**Context:** {sum_data.get('meeting_context', 'N/A')}\n\n"
        
        # Decisions
        md += f"### 2. Key Decisions\n"
        decisions = dec_data.get("decisions", [])
        if decisions:
            for i, d in enumerate(decisions, 1):
                md += f"{i}. **{d.get('title')}**\n"
                md += f"   - *Description:* {d.get('description')}\n"
                md += f"   - *Decider:* {d.get('decider_name')}\n"
                md += f"   - *Status:* {d.get('status', 'Approved')}\n\n"
        else:
            md += "No formal decisions were extracted from this meeting.\n\n"
            
        # Action Items
        md += f"### 3. Action Items & Assignments\n"
        tasks = task_data.get("tasks", [])
        if tasks:
            for i, t in enumerate(tasks, 1):
                md += f"{i}. **{t.get('title')}**\n"
                md += f"   - *Description:* {t.get('description')}\n"
                md += f"   - *Assignee:* {t.get('assignee_name')}\n"
                md += f"   - *Status:* {t.get('status', 'Pending')}\n"
                md += f"   - *Deadline:* {t.get('deadline') or 'N/A'}\n\n"
        else:
            md += "No action items were assigned in this meeting.\n\n"
            
        # Timeline
        md += f"### 4. Roadmap & Milestones\n"
        events = timeline_data.get("events", [])
        if events:
            for e in events:
                md += f"- **[{e.get('event_date')}]** {e.get('description')} (*Project:* {e.get('project_name')})\n"
            md += "\n"
        else:
            md += "No timeline events or project milestones were identified.\n\n"
            
        # Risks
        md += f"### 5. Risk Detection & Mitigations\n"
        risks = risk_data.get("risks", [])
        if risks:
            for i, r in enumerate(risks, 1):
                md += f"{i}. **{r.get('description')}**\n"
                md += f"   - *Severity:* {r.get('impact_level')}\n"
                md += f"   - *Mitigation:* {r.get('mitigation_strategy')}\n\n"
        else:
            md += "No critical risks or blockers were identified.\n\n"

        # Impact & Accountability
        md += f"### 6. Team Impact & Accountability\n"
        md += f"**Community Impact:**\n{impact_data.get('impact_summary', 'N/A')}\n\n"
        md += f"**Accountability Check:**\n{acc_data.get('accountability_summary', 'N/A')}\n\n"
        md += f"**Follow-Up Schedule:** {acc_data.get('follow_up_schedule', 'N/A')}\n\n"

        # Clarifications
        if clar_data.get("is_clarification_needed"):
            md += f"### 7. Open Questions / Ambiguities\n"
            for q in clar_data.get("questions", []):
                md += f"- {q}\n"
            md += "\n"

        return md

    def _build_pdf_report(self, pdf_path: str, title: str, data: Dict[str, Any]) -> None:
        """Draws structured text into a PDF file using fitz (PyMuPDF)."""
        doc = fitz.open()
        
        # Let's create a beautiful document
        # Page size: Letter (612 x 792 points)
        page = doc.new_page(width=612, height=792)
        
        # Margins
        margin = 54
        rect = fitz.Rect(margin, margin, 612 - margin, 792 - margin)
        
        # Draw Title
        y = margin
        page.insert_text(fitz.Point(margin, y), "ActionSync AI Meeting Report", fontsize=20, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 30
        
        page.insert_text(fitz.Point(margin, y), f"Meeting: {title}", fontsize=14, fontname="Helvetica-Bold", color=(0.2, 0.2, 0.2))
        y += 20
        
        page.insert_text(fitz.Point(margin, y), f"Generated: {datetime.date.today().strftime('%B %d, %Y')}", fontsize=10, fontname="Helvetica-Oblique", color=(0.5, 0.5, 0.5))
        y += 30
        
        # Draw Divider Line
        shape = page.new_shape()
        shape.draw_line(fitz.Point(margin, y), fitz.Point(612 - margin, y))
        shape.finish(color=(0.8, 0.8, 0.8), width=1)
        shape.commit()
        y += 25
        
        # Executive Summary Section
        sum_text = data.get("summarizer", {}).get("executive_summary", "No summary.")
        page.insert_text(fitz.Point(margin, y), "1. Executive Summary", fontsize=12, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 15
        
        # Simple text wrapping helper using fitz TextWriter or HTML-like textbox insertion
        tb = fitz.TextWriter(page.rect)
        # We can write text into a textbox which auto-wraps!
        textbox = fitz.Rect(margin, y, 612 - margin, y + 80)
        page.insert_textbox(textbox, sum_text, fontsize=10, fontname="Helvetica", align=fitz.TEXT_ALIGN_LEFT)
        y += 90
        
        # Key Decisions
        page.insert_text(fitz.Point(margin, y), "2. Key Decisions", fontsize=12, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 15
        
        decisions = data.get("decision", {}).get("decisions", [])
        dec_texts = []
        if decisions:
            for d in decisions[:4]:  # Limit to first 4 for single page layout simplicity
                dec_texts.append(f"- {d.get('title')} (Decided by: {d.get('decider_name')})")
        else:
            dec_texts.append("No decisions extracted.")
            
        dec_textbox = fitz.Rect(margin, y, 612 - margin, y + 80)
        page.insert_textbox(dec_textbox, "\n".join(dec_texts), fontsize=10, fontname="Helvetica", align=fitz.TEXT_ALIGN_LEFT)
        y += 90
        
        # Action Items
        page.insert_text(fitz.Point(margin, y), "3. Action Items", fontsize=12, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 15
        
        tasks = data.get("action_item", {}).get("tasks", [])
        task_texts = []
        if tasks:
            for t in tasks[:4]:
                task_texts.append(f"- {t.get('title')} (Assignee: {t.get('assignee_name')}, Deadline: {t.get('deadline') or 'N/A'})")
        else:
            task_texts.append("No tasks assigned.")
            
        task_textbox = fitz.Rect(margin, y, 612 - margin, y + 80)
        page.insert_textbox(task_textbox, "\n".join(task_texts), fontsize=10, fontname="Helvetica", align=fitz.TEXT_ALIGN_LEFT)
        y += 90

        # Timeline and Risks on a second page!
        page2 = doc.new_page(width=612, height=792)
        y = margin
        
        page2.insert_text(fitz.Point(margin, y), "4. Timeline & Project Milestones", fontsize=12, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 15
        
        events = data.get("timeline", {}).get("events", [])
        event_texts = []
        if events:
            for e in events[:5]:
                event_texts.append(f"- [{e.get('event_date')}] {e.get('description')} ({e.get('project_name')})")
        else:
            event_texts.append("No timeline milestones.")
            
        evt_textbox = fitz.Rect(margin, y, 612 - margin, y + 100)
        page2.insert_textbox(evt_textbox, "\n".join(event_texts), fontsize=10, fontname="Helvetica", align=fitz.TEXT_ALIGN_LEFT)
        y += 110
        
        # Risks
        page2.insert_text(fitz.Point(margin, y), "5. Risks & Blockers", fontsize=12, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 15
        
        risks = data.get("risk", {}).get("risks", [])
        risk_texts = []
        if risks:
            for r in risks[:4]:
                risk_texts.append(f"- {r.get('description')} (Severity: {r.get('impact_level')}, Mitigation: {r.get('mitigation_strategy')})")
        else:
            risk_texts.append("No risks identified.")
            
        rsk_textbox = fitz.Rect(margin, y, 612 - margin, y + 100)
        page2.insert_textbox(rsk_textbox, "\n".join(risk_texts), fontsize=10, fontname="Helvetica", align=fitz.TEXT_ALIGN_LEFT)
        y += 110

        # Team Impact & Accountability
        page2.insert_text(fitz.Point(margin, y), "6. Culture, Ethical & Organizational Impact", fontsize=12, fontname="Helvetica-Bold", color=(0.1, 0.3, 0.6))
        y += 15
        
        impact_summary = data.get("community_impact", {}).get("impact_summary", "N/A")
        acc_summary = data.get("accountability", {}).get("accountability_summary", "N/A")
        combined_impact = f"Community Impact:\n{impact_summary}\n\nAccountability Overview:\n{acc_summary}"
        
        impact_textbox = fitz.Rect(margin, y, 612 - margin, y + 150)
        page2.insert_textbox(impact_textbox, combined_impact, fontsize=10, fontname="Helvetica", align=fitz.TEXT_ALIGN_LEFT)
        
        doc.save(pdf_path)
        doc.close()

import datetime
# Register tool
tool_registry.register(DocumentGenerator())

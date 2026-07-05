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
        """Draws structured text into a PDF file using fitz (PyMuPDF) with auto-wrap and pagination."""
        import datetime
        doc = fitz.open()
        
        # Helper to map standard names to fitz short names
        def get_fitz_font(fontname: str) -> str:
            font_key = fontname.lower()
            if "bold" in font_key or font_key == "hebo":
                return "hebo"
            elif "oblique" in font_key or "italic" in font_key or font_key == "heit":
                return "heit"
            else:
                return "helv"
        
        # Helper to wrap text based on font metrics
        def wrap_text_to_width(text: str, fontname: str, fontsize: float, max_width: float) -> list:
            words = str(text).split()
            lines = []
            current_line = []
            fitz_font = get_fitz_font(fontname)
                
            for word in words:
                test_line = " ".join(current_line + [word])
                length = fitz.get_text_length(test_line, fontname=fitz_font, fontsize=fontsize)
                if length <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
                        
            if current_line:
                lines.append(" ".join(current_line))
            return lines

        # Flowable class to manage pagination and coordinates
        class PDFFlowable:
            def __init__(self, doc, width=612, height=792, margin=54):
                self.doc = doc
                self.width = width
                self.height = height
                self.margin = margin
                self.max_y = height - margin
                self.max_width = width - (2 * margin)
                
                self.page = None
                self.y = margin
                self.page_count = 0
                self._new_page()

            def _new_page(self):
                self.page = self.doc.new_page(width=self.width, height=self.height)
                self.page_count += 1
                self.y = self.margin
                
                if self.page_count > 1:
                    self.page.insert_text(
                        fitz.Point(self.margin, self.margin), 
                        "ActionSync AI Meeting Report (Continued)", 
                        fontsize=8, 
                        fontname="heit", 
                        color=(0.5, 0.5, 0.5)
                    )
                    shape = self.page.new_shape()
                    shape.draw_line(fitz.Point(self.margin, self.margin + 8), fitz.Point(self.width - self.margin, self.margin + 8))
                    shape.finish(color=(0.9, 0.9, 0.9), width=0.5)
                    shape.commit()
                    self.y = self.margin + 25

            def add_space(self, amount):
                self.y += amount
                if self.y >= self.max_y:
                    self._new_page()

            def add_text_line(self, text, fontsize=10, fontname="helv", color=(0, 0, 0), leading=12):
                if self.y + leading > self.max_y:
                    self._new_page()
                fitz_font = get_fitz_font(fontname)
                self.page.insert_text(fitz.Point(self.margin, self.y), text, fontsize=fontsize, fontname=fitz_font, color=color)
                self.y += leading

            def add_paragraph(self, text, fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1), leading=11, space_after=6):
                if not text:
                    return
                paragraphs = str(text).split("\n")
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        self.add_space(space_after)
                        continue
                        
                    lines = wrap_text_to_width(para, fontname, fontsize, self.max_width)
                    for line in lines:
                        if self.y + leading > self.max_y:
                            self._new_page()
                        fitz_font = get_fitz_font(fontname)
                        self.page.insert_text(fitz.Point(self.margin, self.y), line, fontsize=fontsize, fontname=fitz_font, color=color)
                        self.y += leading
                    self.add_space(space_after)

        flow = PDFFlowable(doc)
        
        # Professional color palette
        primary_color = (0.07, 0.29, 0.61)  # Deep corporate blue
        secondary_color = (0.2, 0.2, 0.2)
        meta_color = (0.5, 0.5, 0.5)
        
        # 1. Header
        flow.add_text_line("ActionSync AI Meeting Report", fontsize=18, fontname="hebo", color=primary_color, leading=22)
        flow.add_text_line(f"Meeting: {title}", fontsize=12, fontname="hebo", color=secondary_color, leading=16)
        
        meeting_date = datetime.date.today().strftime('%B %d, %Y')
        flow.add_text_line(f"Generated: {meeting_date}", fontsize=9, fontname="heit", color=meta_color, leading=12)
        flow.add_space(8)
        
        # Header separator
        shape = flow.page.new_shape()
        shape.draw_line(fitz.Point(flow.margin, flow.y), fitz.Point(flow.width - flow.margin, flow.y))
        shape.finish(color=(0.8, 0.8, 0.8), width=1)
        shape.commit()
        flow.add_space(15)
        
        # Load sections
        sum_data = data.get("summarizer", {})
        dec_data = data.get("decision", {})
        task_data = data.get("action_item", {})
        risk_data = data.get("risk", {})
        timeline_data = data.get("timeline", {})
        impact_data = data.get("community_impact", {})
        acc_data = data.get("accountability", {})
        clar_data = data.get("clarification", {})
        
        # Section 1: Executive Summary
        flow.add_text_line("1. Executive Summary", fontsize=12, fontname="hebo", color=primary_color, leading=16)
        flow.add_space(4)
        flow.add_paragraph(sum_data.get("executive_summary", "No summary available."), fontsize=9, leading=12)
        
        key_topics = sum_data.get("key_topics", [])
        if key_topics:
            flow.add_paragraph(f"Key Topics: {', '.join(key_topics)}", fontsize=9, fontname="hebo", leading=12)
            
        meeting_context = sum_data.get("meeting_context")
        if meeting_context:
            flow.add_paragraph(f"Context: {meeting_context}", fontsize=9, fontname="heit", leading=12)
        flow.add_space(12)
        
        # Section 2: Key Decisions
        flow.add_text_line("2. Key Decisions", fontsize=12, fontname="hebo", color=primary_color, leading=16)
        flow.add_space(4)
        decisions = dec_data.get("decisions", [])
        if decisions:
            for idx, d in enumerate(decisions, 1):
                title_line = f"{idx}. {d.get('title')} (Status: {d.get('status', 'Approved')})"
                flow.add_text_line(title_line, fontsize=9, fontname="hebo", color=secondary_color, leading=12)
                flow.add_paragraph(f"   Description: {d.get('description')}", fontsize=9, leading=12, space_after=2)
                flow.add_paragraph(f"   Decided by: {d.get('decider_name')}", fontsize=9, fontname="heit", leading=11, space_after=6)
        else:
            flow.add_paragraph("No formal decisions were extracted from this meeting.", fontsize=9, leading=12)
        flow.add_space(12)
        
        # Section 3: Action Items & Assignments
        flow.add_text_line("3. Action Items & Assignments", fontsize=12, fontname="hebo", color=primary_color, leading=16)
        flow.add_space(4)
        tasks = task_data.get("tasks", [])
        if tasks:
            for idx, t in enumerate(tasks, 1):
                deadline_str = f", Deadline: {t.get('deadline')}" if t.get('deadline') else ""
                title_line = f"{idx}. {t.get('title')} (Assignee: {t.get('assignee_name')}{deadline_str})"
                flow.add_text_line(title_line, fontsize=9, fontname="hebo", color=secondary_color, leading=12)
                flow.add_paragraph(f"   Description: {t.get('description')}", fontsize=9, leading=12, space_after=2)
                flow.add_paragraph(f"   Status: {t.get('status', 'Pending')}", fontsize=9, fontname="heit", leading=11, space_after=6)
        else:
            flow.add_paragraph("No action items were assigned in this meeting.", fontsize=9, leading=12)
        flow.add_space(12)
        
        # Section 4: Roadmap & Milestones
        flow.add_text_line("4. Roadmap & Milestones", fontsize=12, fontname="hebo", color=primary_color, leading=16)
        flow.add_space(4)
        events = timeline_data.get("events", [])
        if events:
            for e in events:
                event_line = f"- [{e.get('event_date')}] {e.get('description')} (Project: {e.get('project_name')})"
                flow.add_paragraph(event_line, fontsize=9, leading=12, space_after=4)
        else:
            flow.add_paragraph("No timeline events or project milestones were identified.", fontsize=9, leading=12)
        flow.add_space(12)
        
        # Section 5: Risks & Blockers
        flow.add_text_line("5. Risks & Blockers", fontsize=12, fontname="hebo", color=primary_color, leading=16)
        flow.add_space(4)
        risks = risk_data.get("risks", [])
        if risks:
            for idx, r in enumerate(risks, 1):
                title_line = f"{idx}. {r.get('description')} (Severity: {r.get('impact_level')})"
                flow.add_text_line(title_line, fontsize=9, fontname="hebo", color=secondary_color, leading=12)
                flow.add_paragraph(f"   Mitigation: {r.get('mitigation_strategy')}", fontsize=9, leading=12, space_after=6)
        else:
            flow.add_paragraph("No critical risks or blockers were identified.", fontsize=9, leading=12)
        flow.add_space(12)
        
        # Section 6: Ethical & Organizational Impact
        flow.add_text_line("6. Team Impact & Accountability", fontsize=12, fontname="hebo", color=primary_color, leading=16)
        flow.add_space(4)
        
        impact_summary = impact_data.get("impact_summary")
        if impact_summary:
            flow.add_text_line("Community Impact Summary:", fontsize=9, fontname="hebo", color=secondary_color, leading=12)
            flow.add_paragraph(impact_summary, fontsize=9, leading=12)
            
        acc_summary = acc_data.get("accountability_summary")
        if acc_summary:
            flow.add_text_line("Accountability Overview:", fontsize=9, fontname="hebo", color=secondary_color, leading=12)
            flow.add_paragraph(acc_summary, fontsize=9, leading=12)
            
        follow_up = acc_data.get("follow_up_schedule")
        if follow_up:
            flow.add_paragraph(f"Follow-Up Schedule: {follow_up}", fontsize=9, fontname="hebo", leading=12)
        flow.add_space(12)
        
        # Section 7: Open Questions / Ambiguities
        if clar_data.get("is_clarification_needed") and clar_data.get("questions"):
            flow.add_text_line("7. Open Questions / Ambiguities", fontsize=12, fontname="hebo", color=primary_color, leading=16)
            flow.add_space(4)
            for q in clar_data.get("questions", []):
                flow.add_paragraph(f"- {q}", fontsize=9, leading=12, space_after=4)
                
        doc.save(pdf_path)
        doc.close()

# Register tool
tool_registry.register(DocumentGenerator())

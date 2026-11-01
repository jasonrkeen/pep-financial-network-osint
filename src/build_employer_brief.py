"""Rebuild the reviewed three-page synthetic brief offline from repository inputs."""
from __future__ import annotations

import argparse
import csv
import re
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from pypdf import PdfReader

from .validate_data import load_data, validate


@dataclass(frozen=True)
class BriefConfig:
    """Document settings, separate from analytic assumptions and fixture values."""
    evidence_cutoff: str = "2026-02-01"
    document_date: str = "2026-11-01"
    author: str = "Jason Keen"
    repository_url: str = "https://github.com/jasonrkeen/pep-financial-network-osint"
    pdf_name: str = "JAS-63_PEP_Financial_Network_Employer_Brief.pdf"
    markdown_name: str = "employer_brief.md"


def build_brief(root: Path, output_dir: Path | None = None, config: BriefConfig = BriefConfig()) -> tuple[Path, Path]:
    ROOT = root.resolve()
    output_dir = (output_dir or ROOT / "outputs").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    OUT = output_dir / config.pdf_name
    MD = ROOT / "docs" / config.markdown_name if output_dir == ROOT / "outputs" else output_dir / config.markdown_name
    validation = validate(load_data(ROOT / "data"), config.evidence_cutoff)
    if validation["errors"]:
        raise ValueError("Refusing brief build from invalid synthetic records")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("MIT License\n"):
        raise ValueError("Brief requires the approved MIT license")
    test_report = (ROOT / "outputs/test_results.txt").read_text(encoding="utf-8")
    match = re.search(r"(\d+) passed", test_report)
    if not match or re.search(r"\d+ failed", test_report):
        raise ValueError("A successful recorded test run is required")
    test_count = int(match.group(1))
    tables={}
    for key in ['entities','assets','relationships','transactions']:
        with (ROOT/'data'/('synthetic_'+key+'.csv')).open(newline='',encoding='utf-8') as stream:
            tables[key]=list(csv.DictReader(stream))

    text_sections=[]
    styles={
     'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10.6,leading=14.5,textColor=colors.HexColor('#202020'),spaceAfter=9),
     'small':ParagraphStyle('small',fontName='Helvetica',fontSize=9,leading=12,textColor=colors.HexColor('#353535')),
     'heading':ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=12.3,leading=16,textColor=colors.black),
    }
    c=canvas.Canvas(str(OUT),pagesize=(612,792),pageCompression=1,invariant=1)
    c.setTitle('PEP Financial Network OSINT Employer Portfolio Brief')
    c.setAuthor(config.author)
    c.setSubject('Synthetic evidence-disciplined financial network implementation')

    def paragraph(text: str, x: float, y: float, width: float, kind: str = 'body', gap: float = 9) -> float:
        p=Paragraph(text,styles[kind]);w,h=p.wrap(width,1000)
        p.drawOn(c,x,y-h)
        return y-h-gap

    def heading(text: str, x: float, y: float, width: float) -> float:
        return paragraph(text,x,y,width,'heading',gap=7)

    def footer(number: int, width: float) -> None:
        c.setFillColor(colors.HexColor('#555555'));c.setFont('Helvetica',8.2)
        c.drawString(48,28,f'{config.author}  |  Synthetic portfolio  |  Evidence cutoff {config.evidence_cutoff}')
        c.drawRightString(width-48,28,f'{number} / 3')

    def block(title: str, body: str, x: float, y: float, width: float) -> float:
        text_sections.append((title,body))
        y=heading(title,x,y,width)
        return paragraph(body,x,y,width)

    # Page one: scope, analytic question and the complete workflow.
    c.setFillColor(colors.black);c.setFont('Helvetica-Bold',22)
    c.drawString(48,736,'PEP Financial Network OSINT')
    c.setFont('Helvetica',12);c.drawString(48,714,'Employer portfolio brief')
    c.setFont('Helvetica',10);c.drawString(48,693,f'{config.author}  |  Updated {config.document_date}  |  Synthetic portfolio')
    y=667
    opening='This portfolio demonstrates a reproducible financial-intelligence workflow using a fictional PEP, companies, banks, transactions and assets. Its central result is an auditable record of what the evidence supports, what it does not establish, and what additional collection is needed. The project is a worked implementation layer; it does not claim universal methodology validity or formal operational intelligence experience.'
    text_sections.append(('Purpose',opening));y=paragraph(opening,48,y,516)
    y=block('The analytic question','Which entities, flows, assets and intermediaries can be linked, and what supports ownership, control, access, benefit or mere association? Public-record networks can overstate attribution when different propositions are collapsed into a single relationship. This demo keeps shareholding, family ties, directorship, payments, asset association, succession and title separate.',48,y-3,516)
    y=heading('The workflow',48,y-3,516)
    workflow='Requirements > entity resolution > ownership and control > transactions > asset linkage > corporate succession and title > confidence and unknowns > collection gaps.'
    text_sections.append(('The workflow',workflow));y=paragraph(workflow,48,y,516)
    stages='The requirements fix the question, evidence cutoff and synthetic scope. Entity resolution uses stable IDs and registration keys; name similarity never merges records automatically. Dated relationships separate current from historical shareholding. Transaction records retain currencies, purpose and bank context. Asset linkage compares counterparties and timing, while title is assessed separately from legal succession. The validator rejects a chronology-based funding inference if the transfer follows purchase or the payee is not the purchaser. Every claim retains its sources, qualification, competing explanation and next evidence where needed.'
    y=paragraph(stages,48,y,516);text_sections.append(('How it operates',stages))
    y=block('What the demonstration establishes','Dana Mercer is the documented shareholder of Northbridge Holdings. Alex Mercer is a family member, but that relation does not establish his ownership. A USD 4.0 million intercompany loan reaches Meridian Property SPV 17 days before its USD 5.5 million property purchase. The timing is compatible with a contribution to acquisition liquidity; no record earmarks the transfer to the property. A later merger is documented, but current asset-specific title and trust beneficiaries remain unresolved.',48,y-3,516)
    y=paragraph('<b>Outputs:</b> a typed network graph, nine-claim evidence matrix, source register and dependency table, unresolved collection gaps, validation reports and reproducible inputs.',48,y,516,'small')
    assert y>55,('Page 1 overflow',y)
    footer(1,612);c.showPage()

    # Page two: a full vector redraw of all 12 nodes and all 14 typed edges.
    c.setPageSize((792,612));c.setFillColor(colors.black);c.setFont('Helvetica-Bold',19)
    c.drawString(45,566,'Synthetic financial network')
    c.setFont('Helvetica',10);c.drawString(45,547,'All names and records depict fictional scenario roles  |  Evidence cutoff 2026-02-01')
    pos={'P001':(82,447),'P002':(195,447),'C001':(305,447),'P003':(195,330),'C002':(305,330),
         'C003':(455,330),'C004':(602,330),'T001':(602,447),'B001':(710,447),
         'B002':(305,207),'A001':(455,207),'A002':(125,207)}
    COL={'ownership':'#39724d','family':'#777777','director':'#777777','bank_context':'#8b8b8b','address':'#777777','transaction':'#216b9b','merger':'#795390','purchase':'#a06b1a'}

    def arrow(u: str, v: str, kind: str, offset: float = 0, historical: bool = False) -> None:
        x1,y1=pos[u];x2,y2=pos[v];dx=x2-x1;dy=y2-y1
        length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
        # Trim against the rectangular node boxes; vertical margin is smaller.
        trim=min(48/abs(ux) if ux else 1e9,25/abs(uy) if uy else 1e9)
        sx,sy=x1+ux*trim,y1+uy*trim;ex,ey=x2-ux*trim,y2-uy*trim
        color=colors.HexColor(COL[kind]);c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(1.2)
        c.setDash([4,3] if historical or kind in {'family','director','purchase','merger'} else ([1,3] if kind in {'bank_context','address'} else []))
        p=c.beginPath();p.moveTo(sx,sy)
        cx1=sx+dx*.25-uy*offset;cy1=sy+dy*.25+ux*offset
        cx2=ex-dx*.25-uy*offset;cy2=ey-dy*.25+ux*offset
        p.curveTo(cx1,cy1,cx2,cy2,ex,ey);c.drawPath(p)
        c.setDash([])
        ax,ay=ex-cx2,ey-cy2;al=math.hypot(ax,ay);ax,ay=ax/al,ay/al
        p=c.beginPath();p.moveTo(ex,ey);p.lineTo(ex-ax*6-ay*2.6,ey-ay*6+ax*2.6);p.lineTo(ex-ax*6+ay*2.6,ey-ay*6-ax*2.6);p.close();c.drawPath(p,fill=1,stroke=0)

    for row in tables['relationships']:
        offset={'R003':-15,'R005':30,'R008':-30}.get(row['relationship_id'],0)
        arrow(row['source_entity_id'],row['target_entity_id'],row['relationship_type'],offset,row['temporal_status']=='Historical')
    for row in tables['transactions']:
        arrow(row['payer_entity_id'],row['payee_entity_id'],'transaction',{'TX001':38,'TX003':-38,'TX002':15}.get(row['transaction_id'],0))
    for row in tables['assets']:
        arrow(row['associated_entity_id'],row['asset_id'],'purchase' if row['association_basis']=='purchase_record' else 'address')
    assert set(pos) == {r['entity_id'] for r in tables['entities']} | {r['asset_id'] for r in tables['assets']}, 'Brief layout must account for every node'
    assert len(tables['relationships'])+len(tables['transactions'])+len(tables['assets'])==14, 'Review the fixed demo layout when edges change'

    node_lines={
     'P001':['DEMO Alex Mercer','PEP role','No ownership attribution'], 'P002':['DEMO Dana Mercer','Family member'],
     'P003':['DEMO Elias Voss','Director'], 'C001':['DEMO Northbridge','Holdings Ltd'],
     'C002':['DEMO Harbor Crest','Trading Ltd'], 'C003':['DEMO Meridian','Property SPV Ltd'],
     'C004':['DEMO Summit','Residential Management','LLC'], 'T001':['DEMO Alder Family Trust','Beneficiaries unknown'],
     'B001':['DEMO Continental','Private Bank'], 'B002':['DEMO Eastport','Commercial Bank'],
     'A001':['DEMO 14 Meridian','Square','Current title unresolved'], 'A002':['DEMO Ridgeview','Residence','Address association only'],
    }
    types={row['entity_id']:row['entity_type'] for row in tables['entities']}
    fills={'person':'#e0edf5','company':'#e1eddf','trust':'#eee3f5','bank':'#eeeeee','asset':'#fcf0cf'}
    for node,(x,y0) in pos.items():
        c.setFillColor(colors.HexColor(fills[types.get(node,'asset')]));c.setStrokeColor(colors.HexColor('#a5a5a5'));c.setLineWidth(.6)
        c.roundRect(x-48,y0-25,96,50,5,fill=1,stroke=1)
        lines=node_lines[node];c.setFillColor(colors.black)
        for i,line in enumerate(lines):
            c.setFont('Helvetica-Bold' if i==0 else 'Helvetica',7.5)
            c.drawCentredString(x,y0+(len(lines)-1)*4.7-i*9.4-2.3,line)

    labels={
     'R001':(250,481,['100% shares','current'],'ownership'),
     'R002':(138,481,['family only'],'family'),
     'R003':(255,405,['100% shares','current'],'ownership'),
     'R004':(249,343,['director only'],'director'),
     'R005':(527,377,['legal merger','A001 title unresolved'],'merger'),
     'R006':(653,391,['100% shares','current'],'ownership'),
     'R007':(270,260,['account context'],'bank_context'),
     'R008':(530,277,['100% shares','historical'],'ownership'),
     'TX001':(386,372,['TX001  USD 4.0m','2025-02-03  loan','transfer only'],'transaction'),
     'TX002':(348,413,['TX002  EUR 1.2m','working capital','transfer only'],'transaction'),
     'TX003':(383,276,['TX003  USD 750k','purpose unknown','transfer only'],'transaction'),
     'TX004':(656,497,['TX004  USD 2.5m','source of funds unresolved','transfer only'],'transaction'),
     'A001':(492,258,['historical purchase','current title unresolved'],'purchase'),
     'A002':(209,246,['shared address only'],'address'),
    }
    for key,(x,y0,lines,kind) in labels.items():
        for i,line in enumerate(lines):
            width=c.stringWidth(line,'Helvetica',7.4)
            c.setFillColor(colors.white);c.rect(x-width/2-1,y0-i*9-2,width+2,9,fill=1,stroke=0)
            c.setFillColor(colors.HexColor(COL[kind]));c.setFont('Helvetica',7.4);c.drawCentredString(x,y0-i*9,line)
    c.setFillColor(colors.black);c.setFont('Helvetica',8.5)
    c.drawString(45,161,'Green: shares  |  Blue: transfers  |  Purple: merger  |  Gold: historical purchase')
    c.drawString(45,147,'Gray: association or role  |  Dashed green: historical shares  |  Dotted gray: address or account context')
    y=127
    y=paragraph('<b>Read each edge by its type.</b> Family and shared address do not establish ownership. Transfers do not prove property funding. Historical purchase does not establish current title. Merger succession does not identify an asset-specific title transfer.',45,y,702,'small',7)
    y=paragraph('The graph retains all 12 nodes and 14 typed edges. Rejected ownership/funding propositions and unresolved beneficiary/title claims remain in the evidence matrix; they are not attribution edges. The layout is adapted from the validated demo without changing its nodes or relationships.',45,y,702,'small',3)
    assert y>45,('Page 2 overflow',y)
    footer(2,792);c.showPage()

    # Page three: evidence model, outcomes, limits and skills.
    c.setPageSize((612,792));c.setFillColor(colors.black);c.setFont('Helvetica-Bold',19)
    c.drawString(48,737,'Evidence discipline and reproducibility')
    y=711
    y=block('Confidence and open questions','The claims ledger distinguishes Confirmed, Strongly supported, Probable / analytic judgment, Alleged / unverified, Unresolved and Rejected. Confidence is qualitative and specific to the proposition, not a legal probability. Evidence maturity is separate: Established, Corroborated, Analytic or Open dependency; Experimental is a reserved label with no scoring implementation.',48,y,516)
    y=paragraph('S005 summarizes S004, so the two count as one documented source family rather than independent corroboration. CL007 needs an asset-specific merger transfer schedule and post-merger title extract. CL009 needs a trust deed or verified beneficiary record. TX004 needs originating-account records to resolve the economic source of funds. Rejected means unsupported on this bounded record, not disproven for all time.',48,y,516)
    text_sections.append(('Source lineage and collection gaps','S005 derives from S004. CL007 requires asset-specific transfer/title evidence; CL009 requires beneficiary records; TX004 requires economic source-of-funds evidence. Rejected means unsupported on the bounded record.'))
    y=heading('Executed validation',48,y-1,516)
    data=[['Check','Recorded result'],['Automated tests',f'{test_count} passed, including all 14 frozen controls'],['Clean synthetic inputs','0 errors; 1 expected derivative-context warning'],['Intentionally broken inputs','24 errors; validator exits 1; graph build refused'],['Generated artifacts','12 nodes; 14 edges; 9 claims; GraphML round-trip passed'],['Repeated local builds','Input hashes recorded; repeated output hashes match']]
    table=Table([[Paragraph(escape(value),styles['small']) for value in row] for row in data],colWidths=[154,362])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3e9ed')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    w,h=table.wrap(516,1000);table.drawOn(c,48,y-h);y-=h+12
    text_sections.append(('Executed validation',f'{test_count} tests passed, including 14 frozen controls; clean 0 errors; broken 24 errors; graph refused broken inputs; 12 nodes / 14 edges / 9 claims; GraphML round-trip and repeated hashes passed.'))
    y=block('Technical stack and limitations','Python, NetworkX, CSV and GraphML support a reproducible offline demo, with pinned dependencies, an input SHA-256 manifest and automated GitHub checks. The validator checks IDs, temporal ownership, currency aggregation, funding versus valuation, lineage, attribution and visible dependencies. The CI workflow reruns these controls. A hostile self-review corrected misleading labels and evidence-link weaknesses; it was not an independent audit.',48,y,516)
    y=paragraph('All records are synthetic. Validation cannot authenticate documents, discover undisclosed copying, verify foreign law or establish real-world beneficial ownership. No experimental weights or legal scores are used. A purchase price is not current market value; offshore location and PEP status do not imply misconduct.',48,y,516)
    text_sections.append(('Guardrails and limitations','All records are synthetic. Validation cannot authenticate documents, discover undisclosed copying, verify foreign law or establish real-world beneficial ownership. No experimental weights or legal scores are used. A purchase price is not current market value; offshore location and PEP status do not imply misconduct.'))
    y=block('Skills demonstrated','Requirements framing, OSINT evidence qualification, due diligence, AML and financial-crime reasoning, entity resolution, transaction analysis, network analysis, uncertainty management and reproducible research. The portfolio shows how explicit evidence boundaries support a reviewable intelligence product and focused next collection.',48,y-1,516)
    link=config.repository_url
    reference=f'<b>Public implementation:</b> <link href="{link}" color="#175b85">jasonrkeen/pep-financial-network-osint</link>. Execution evidence: outputs/test_results.txt, verification_summary.json and validation reports; interpretation: evidence_matrix.csv, unresolved_gaps.csv and docs/red_team_review.md. MIT License, copyright 2026 Jason Keen. Published November 1, 2026, following owner approval and public-access verification. All demonstration records remain fictional.'
    y=paragraph(reference,48,y,516,'small',0)
    assert y>50,('Page 3 overflow',y)
    footer(3,612);c.save()


    # Export the complete prose, not a shortened or reordered second brief.
    reader = PdfReader(str(OUT))
    if len(reader.pages) != 3:
        raise ValueError("Employer brief must remain three pages")
    extracted = "\n".join(page.extract_text() for page in reader.pages)
    for required in ["CL007", "CL009", "TX004", f"{test_count} passed", "24 errors", "MIT License", "Public implementation"]:
        if required.lower() not in extracted.lower():
            raise ValueError("Missing brief content: " + required)
    # Page 2's complete network remains a linked figure in the editable prose.
    prose = "# PEP Financial Network OSINT\n\nEmployer portfolio brief | " + config.author + " | Updated " + config.document_date + "\n\n"
    for page, title in [(reader.pages[0], "Workflow and demonstration"), (reader.pages[2], "Evidence discipline and reproducibility")]:
        prose += "## " + title + "\n\n" + page.extract_text().rsplit(config.author, 1)[0].strip() + "\n\n"
    prose += "## Complete synthetic network\n\n![All 12 fictional nodes and 14 typed edges](../outputs/demo_network.png)\n\n"
    prose += "The PDF contains the complete graph in a brief-sized vector layout. Family and address association do not establish ownership; payments do not prove funding; merger does not prove asset-specific title.\n\n"
    prose += "## License and publication\n\n[MIT License](../LICENSE), copyright 2026 Jason Keen. [Public implementation repository](" + config.repository_url + ") published November 1, 2026, following owner approval and unauthenticated access verification. All demonstration records remain fictional.\n"
    MD.write_text(prose, encoding="utf-8", newline="\n")
    return OUT, MD


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    pdf, markdown = build_brief(root, args.output)
    print(f"Brief generated: {pdf.name}; editable prose: {markdown.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Script to generate a sample tender PDF for testing.
Creates a realistic government construction tender document.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from app.config import SAMPLE_TENDERS_DIR


def create_sample_tender():
    """Generate a sample government construction tender PDF."""
    output_path = SAMPLE_TENDERS_DIR / "sample_highway_construction_tender.pdf"

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, spaceBefore=15, spaceAfter=8)
    body_style = ParagraphStyle('Body2', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6, leading=14)
    center_style = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)

    story = []

    # Cover Page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("GOVERNMENT OF INDIA", center_style))
    story.append(Paragraph("MINISTRY OF ROAD TRANSPORT AND HIGHWAYS", center_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("TENDER DOCUMENT", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Construction of 4-Lane National Highway", center_style))
    story.append(Paragraph("NH-48 Section: Km 120.000 to Km 185.000", center_style))
    story.append(Paragraph("(Under Bharatmala Pariyojana Phase-II)", center_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Tender Reference: MORTH/NH48/2025/BMP-II/0847", center_style))
    story.append(Paragraph("Estimated Cost: INR 1,245.67 Crore", center_style))
    story.append(Paragraph("Bid Submission Deadline: 15th March 2025", center_style))
    story.append(PageBreak())

    # Section 1: Scope of Work
    story.append(Paragraph("SECTION 1: SCOPE OF WORK", heading_style))
    story.append(Paragraph(
        "1.1 The scope of work includes the design, construction, and completion of a 4-lane divided "
        "highway with paved shoulders from Km 120.000 to Km 185.000 on National Highway NH-48. The "
        "project includes construction of bridges, flyovers, underpasses, service roads, toll plazas, "
        "and all associated infrastructure.", body_style))
    story.append(Paragraph(
        "1.2 The Contractor shall be responsible for obtaining all necessary environmental clearances "
        "from the Ministry of Environment, Forest and Climate Change (MoEFCC) and State Pollution "
        "Control Board (SPCB) before commencing construction activities.", body_style))
    story.append(Paragraph(
        "1.3 The project traverses through agricultural land, forest areas (approximately 12 hectares "
        "of forest diversion required), and semi-urban settlements. The Contractor shall ensure minimal "
        "disruption to existing communities and ecosystems.", body_style))

    # Section 2: Environmental Clauses (some strong, some vague)
    story.append(Paragraph("SECTION 2: ENVIRONMENTAL REQUIREMENTS", heading_style))
    story.append(Paragraph(
        "2.1 Environmental Impact Assessment: The Contractor shall comply with the EIA Notification "
        "2006 (as amended) and obtain Environmental Clearance (EC) from MoEFCC. An Environmental "
        "Management Plan (EMP) shall be submitted within 60 days of contract award.", body_style))
    story.append(Paragraph(
        "2.2 Dust Control: During construction, the Contractor shall implement dust suppression "
        "measures including water sprinkling at least twice daily on all active construction areas, "
        "access roads, and material storage sites. Wind barriers of minimum 3m height shall be "
        "erected around all crushing and batching plants.", body_style))
    story.append(Paragraph(
        "2.3 Noise Control: Construction activities generating noise levels above 75 dB(A) at the "
        "nearest habitation shall be restricted to daytime hours (7:00 AM to 6:00 PM). The Contractor "
        "shall maintain noise monitoring records and submit monthly reports.", body_style))
    story.append(Paragraph(
        "2.4 Tree Plantation: The Contractor shall plant trees along the highway corridor as per "
        "the approved plantation plan. A minimum of 3 trees shall be planted for every tree felled "
        "during construction. The survival rate shall be maintained at 80% for a period of 3 years.", body_style))
    story.append(Paragraph(
        "2.5 The Contractor should generally follow good environmental practices during "
        "construction activities.", body_style))  # Intentionally vague clause

    # Section 3: Waste Management
    story.append(Paragraph("SECTION 3: WASTE MANAGEMENT", heading_style))
    story.append(Paragraph(
        "3.1 Construction and Demolition Waste: The Contractor shall prepare a Construction and "
        "Demolition (C&D) Waste Management Plan in compliance with the C&D Waste Management Rules, "
        "2016. A minimum of 50% of C&D waste shall be recycled or reused on-site.", body_style))
    story.append(Paragraph(
        "3.2 Hazardous Waste: All hazardous wastes including used oil, bitumen residue, chemical "
        "containers, and contaminated soil shall be disposed of through authorized recyclers/treatment "
        "facilities as per the Hazardous and Other Wastes (Management and Transboundary Movement) "
        "Rules, 2016.", body_style))
    story.append(Paragraph(
        "3.3 The Contractor shall ensure proper waste disposal at the construction site.", body_style))  # Vague

    # Section 4: Material Specifications (some sustainability mentions)
    story.append(Paragraph("SECTION 4: MATERIAL SPECIFICATIONS", heading_style))
    story.append(Paragraph(
        "4.1 The Contractor shall use BIS-certified materials conforming to relevant Indian Standards. "
        "Preference shall be given to locally sourced materials to reduce transportation emissions.", body_style))
    story.append(Paragraph(
        "4.2 Fly Ash Utilization: In compliance with the MOEF notification on fly ash utilization, "
        "the Contractor shall use fly ash-based products (bricks, cement, embankment fill) wherever "
        "technically feasible. A minimum of 25% fly ash shall be blended in cement used for "
        "non-structural applications.", body_style))
    story.append(Paragraph(
        "4.3 Reclaimed Asphalt Pavement (RAP): Where existing pavement is being removed, the "
        "Contractor shall reclaim and recycle a minimum of 30% of the asphalt material for use "
        "in new pavement layers.", body_style))

    story.append(PageBreak())

    # Section 5: Water Management
    story.append(Paragraph("SECTION 5: WATER MANAGEMENT", heading_style))
    story.append(Paragraph(
        "5.1 Water Conservation: The Contractor shall implement water conservation measures at all "
        "construction camps and batching plants. Recycling of wash water from ready-mix concrete "
        "plants is mandatory.", body_style))
    story.append(Paragraph(
        "5.2 Stormwater Management: The highway design shall incorporate adequate stormwater drainage "
        "systems including cross-drainage structures, roadside drains, and retention ponds at "
        "critical locations.", body_style))
    story.append(Paragraph(
        "5.3 Ground Water Protection: The Contractor shall not extract groundwater beyond the limits "
        "specified in the Central Ground Water Authority (CGWA) No Objection Certificate. Tube well "
        "installations require prior CGWA approval.", body_style))

    # Section 6: Safety and Labor (minimal sustainability)
    story.append(Paragraph("SECTION 6: HEALTH AND SAFETY", heading_style))
    story.append(Paragraph(
        "6.1 The Contractor shall comply with all applicable labor laws and safety regulations. "
        "Personal Protective Equipment (PPE) shall be provided to all workers at the construction site.", body_style))
    story.append(Paragraph(
        "6.2 A Safety Officer shall be appointed full-time at the project site.", body_style))

    # Section 7: Quality Assurance (no sustainability)
    story.append(Paragraph("SECTION 7: QUALITY ASSURANCE", heading_style))
    story.append(Paragraph(
        "7.1 The Contractor shall establish a Quality Assurance laboratory at the project site "
        "equipped with all testing equipment as per MORTH specifications.", body_style))
    story.append(Paragraph(
        "7.2 Third-party quality audits shall be conducted quarterly.", body_style))

    # Section 8: Financial Terms
    story.append(Paragraph("SECTION 8: FINANCIAL TERMS", heading_style))
    story.append(Paragraph(
        "8.1 The bid shall be evaluated on the basis of the lowest quoted price (L1 system). "
        "No additional weightage is given for environmental or sustainability criteria in "
        "bid evaluation.", body_style))  # This is a gap - no LCC or green criteria in evaluation
    story.append(Paragraph(
        "8.2 Performance Bank Guarantee of 5% of contract value shall be submitted.", body_style))

    # Build PDF
    doc.build(story)
    print(f"Sample tender PDF created: {output_path}")
    return output_path


def create_sample_urban_tender():
    """Generate a second sample - urban development tender."""
    output_path = SAMPLE_TENDERS_DIR / "sample_smart_city_tender.pdf"

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, spaceBefore=15, spaceAfter=8)
    body_style = ParagraphStyle('Body2', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6, leading=14)
    center_style = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)

    story = []

    # Cover
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("SMART CITY MISSION", center_style))
    story.append(Paragraph("MUNICIPAL CORPORATION OF GREATER MUMBAI", center_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("TENDER FOR INTEGRATED COMMAND AND CONTROL CENTER", title_style))
    story.append(Paragraph("With Smart Infrastructure and Urban Services", center_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Tender No: MCGM/SC/ICCC/2025/1234", center_style))
    story.append(Paragraph("Estimated Cost: INR 478.50 Crore", center_style))
    story.append(PageBreak())

    # Scope
    story.append(Paragraph("SECTION 1: PROJECT OVERVIEW", heading_style))
    story.append(Paragraph(
        "1.1 This tender covers the design, development, implementation and maintenance of an "
        "Integrated Command and Control Center (ICCC) for the city, including smart street lighting "
        "with LED technology, intelligent traffic management system, environmental sensors network, "
        "and citizen grievance redressal platform.", body_style))

    # Energy
    story.append(Paragraph("SECTION 2: ENERGY AND SUSTAINABILITY", heading_style))
    story.append(Paragraph(
        "2.1 Smart Street Lighting: All street lights shall be replaced with LED luminaires with "
        "a minimum efficacy of 120 lumens/watt. The system shall include dimming controls to reduce "
        "energy consumption by 30% during off-peak hours (11 PM to 5 AM).", body_style))
    story.append(Paragraph(
        "2.2 Solar Energy Integration: The ICCC building shall incorporate rooftop solar panels "
        "with a minimum capacity of 100 kWp. The building shall target IGBC Gold certification.", body_style))
    story.append(Paragraph(
        "2.3 The data center cooling system shall achieve a Power Usage Effectiveness (PUE) "
        "of 1.5 or better.", body_style))
    story.append(Paragraph(
        "2.4 Environmental Monitoring: A network of 50 environmental sensors shall be deployed "
        "across the city to monitor PM2.5, PM10, NO2, SO2, O3, temperature, and humidity in "
        "real-time. Data shall be publicly accessible through a citizen dashboard.", body_style))

    # E-Waste
    story.append(Paragraph("SECTION 3: E-WASTE AND LIFECYCLE", heading_style))
    story.append(Paragraph(
        "3.1 All IT equipment suppliers must provide EPR (Extended Producer Responsibility) "
        "certificates and commit to end-of-life take-back of all supplied hardware.", body_style))
    story.append(Paragraph(
        "3.2 Equipment lifecycle shall be considered in bid evaluation with a minimum expected "
        "operational life of 7 years for all hardware components.", body_style))
    story.append(Paragraph(
        "3.3 The Contractor shall provide a comprehensive e-waste management plan.", body_style))

    # Evaluation (better than highway - has some green criteria)
    story.append(Paragraph("SECTION 4: BID EVALUATION CRITERIA", heading_style))
    story.append(Paragraph(
        "4.1 Technical evaluation (70%) shall include: Solution Architecture (25%), "
        "Implementation Plan (20%), Team Composition (15%), and Sustainability & Green "
        "Features (10%).", body_style))
    story.append(Paragraph(
        "4.2 Financial evaluation shall carry 30% weightage based on lowest price methodology.", body_style))
    story.append(Paragraph(
        "4.3 Bidders with ISO 14001 certification shall receive 2 additional marks in "
        "technical evaluation.", body_style))

    doc.build(story)
    print(f"Sample tender PDF created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_sample_tender()
    create_sample_urban_tender()
    print("All sample tenders generated!")

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import FootfallData
from services.report_generator import ReportGeneratorEngine

router = APIRouter(prefix="/reports", tags=["Reports & Export"])
reporter = ReportGeneratorEngine()

@router.get("/export")
def export_reports(
    format: str = Query("pdf", description="pdf, excel, csv"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    store_id = current_user.store_id or 1
    
    # Query sample report data
    records = db.query(FootfallData).filter(FootfallData.store_id == store_id).order_by(FootfallData.timestamp.desc()).limit(30).all()
    
    data_list = [
        {
            "Timestamp": r.timestamp.strftime("%Y-%m-%d %H:00"),
            "Footfall_Count": r.count,
            "Temperature_C": r.temperature,
            "Rainfall_mm": r.rain_mm,
            "Is_Holiday": "Yes" if r.is_holiday else "No",
            "Promotion_Active": "Yes" if r.promotion_active else "No"
        } for r in records
    ]

    summary_metrics = {
        "Total Footfall (30h)": sum(r.count for r in records) if records else 4500,
        "Average Hourly Traffic": round(sum(r.count for r in records)/len(records), 1) if records else 150.0,
        "Peak Footfall": max(r.count for r in records) if records else 380,
        "Store ID": f"Store #{store_id}"
    }

    if format == "csv":
        csv_data = reporter.generate_csv_report(data_list)
        return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=retailsense_report.csv"})
    elif format == "excel":
        excel_bytes = reporter.generate_excel_report(data_list)
        return Response(content=excel_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=retailsense_report.xlsx"})
    else:  # pdf
        pdf_bytes = reporter.generate_pdf_report("RetailSense AI Daily Executive Report", summary_metrics, data_list)
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=retailsense_report.pdf"})

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from ml.data_pipeline import generate_synthetic_footfall_df
from ml.explainable_ai import ExplainableAIEngine
from ml.footfall_models import FootfallPredictorEngine, FEATURE_COLS

router = APIRouter(prefix="/explainability", tags=["Explainable AI (XAI)"])

@router.get("/shap")
def get_shap_explanation(current_user = Depends(get_current_user)):
    """
    Returns SHAP feature attribution scores explaining the primary drivers of footfall predictions.
    """
    # Generate background & sample prediction instance
    df = generate_synthetic_footfall_df(days=7)
    predictor = FootfallPredictorEngine()
    
    # Train light model for fast response
    X = df[FEATURE_COLS]
    y = df['count']
    model = predictor.train_xgboost(X.iloc[:-24], y.iloc[:-24], X.iloc[-24:], y.iloc[-24:])
    
    explainer = ExplainableAIEngine(model, df)
    shap_res = explainer.get_shap_explanation(X.iloc[[-1]])
    lime_res = explainer.get_lime_explanation(X.iloc[[-1]])

    return {
        "xai_framework": "SHAP (SHapley Additive exPlanations) & LIME",
        "shap_summary": shap_res,
        "lime_rules": lime_res
    }

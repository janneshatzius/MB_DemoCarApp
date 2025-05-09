# core/recommendation_service.py
from data.load_recommendations_repository import (
    fetch_recommendations,
    fetch_all_recommendations
)

class RecommendationService:

    @staticmethod
    def get_all(dealership_id: int):
        """Return every Recommendation row for this dealership (on startup)."""
        return fetch_recommendations(dealership_id)

    @staticmethod
    def search_exact(
        raw_query: str,
        dealership_id: int,
        column: str = "all"
    ):
        """
        raw_query: comma-separated exact terms, e.g. "Citan Tourer, V-Klasse"
        column: one of "all", "gssn_id", "car_model_name", "recommendation_source"
        
        If raw_query is non-empty, search *all* rows in the table,
        otherwise just return the default dealership slice.
        """
        q = raw_query.strip()
        if q:
            df = fetch_all_recommendations()      # <-- load everything
        else:
            df = fetch_recommendations(dealership_id)

        if not q:
            return df

        terms = [t.strip() for t in q.split(",") if t.strip()]
        mask = False

        if column == "all":
            for term in terms:
                mask |= df["gssn_id"].eq(term)
                mask |= df["car_model_name"].eq(term)
                mask |= df["recommendation_source"].astype(str).eq(term)
        else:
            series = (
                df[column].astype(str)
                if column == "recommendation_source"
                else df[column]
            )
            term_mask = False
            for term in terms:
                term_mask |= series.eq(term)
            mask = term_mask

        return df[mask]

import math

# --- Data / Knowledge Base ---
# Common Overall Heat Transfer Coefficients (Approximate values in W/m²K)
U_GUIDELINES = {
    "Water - Water": 1200,
    "Water - Oil": 350,
    "Steam - Water": 2500,
    "Steam - Oil": 170,
    "Air - Water": 150,
    "Ammonia - Water": 1500,
}


def calculate_hx_area(Q, U, dT_lm):
    """
    Calculates the Heat Exchanger Area.
    Formula: A = Q / (U * dT_lm)
    """
    try:
        # Avoid division by zero
        if U == 0 or dT_lm == 0:
            return "Error: U and dT_lm must be non-zero."

        area = Q / (U * dT_lm)
        return round(area, 4)
    except Exception as e:
        return f"Calculation Error: {e}"


def calculate_heat_load(U, A, dT_lm):
    """
    Calculates the Heat Load (Q).
    Formula: Q = U * A * dT_lm
    """
    return round(U * A * dT_lm, 4)

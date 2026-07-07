from fastapi import HTTPException

VALID_GENDERS = {"Male", "Female"}

VALID_CONTRACTS = {
    "Month-to-month",
    "One year",
    "Two year"
}


def validate_customer(customer):

    if customer["tenure"] < 0:
        raise HTTPException(
            status_code=400,
            detail="Tenure não pode ser negativo."
        )

    if customer["MonthlyCharges"] < 0:
        raise HTTPException(
            status_code=400,
            detail="MonthlyCharges inválido."
        )

    if customer["TotalCharges"] < 0:
        raise HTTPException(
            status_code=400,
            detail="TotalCharges inválido."
        )

    if customer["gender"] not in VALID_GENDERS:
        raise HTTPException(
            status_code=400,
            detail="Gender inválido."
        )

    if customer["Contract"] not in VALID_CONTRACTS:
        raise HTTPException(
            status_code=400,
            detail="Tipo de contrato inválido."
        )
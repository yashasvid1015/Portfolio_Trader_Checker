
import csv
from portfolio_data import portfolios


def check_trade(trade):

    portfolio = portfolios.get(trade["portfolio_id"])

    if portfolio is None:
        return "Rejected", "Portfolio not found."

    # Step 1: Validate trade data
    try:
        quantity = float(trade["quantity"])
        price = float(trade["price"])
    except (ValueError, TypeError):
        return "Rejected", "Invalid trade data."

    action = trade["action"]

    if quantity <= 0 or price <= 0 or action not in ["Buy", "Sell"]:
        return "Rejected", "Invalid trade data."

    security_id = trade["security_id"]

    holdings = portfolio["current_holdings"]

    # Find existing holding
    existing_quantity = 0

    for holding in holdings:
        if holding["security_id"] == security_id:
            existing_quantity = holding["quantity"]
            break

    # Step 2: Restricted security check
    if security_id in portfolio["restricted_securities"]:
        return "Rejected", "Security is restricted for this portfolio."

    # Step 3: Sell check
    if action == "Sell":
        if existing_quantity < quantity:
            return "Rejected", "Insufficient holdings to sell."

        return "Approved", "Trade passed all compliance checks."

    # Step 4: Buy affordability check
    cash = portfolio["cash_balance"]
    trade_value = quantity * price

    if trade_value > cash:
        return "Rejected", "Insufficient cash for this buy order."

    # Step 5: Position concentration check (Buy only)

    post_trade_cash = cash - trade_value

    post_trade_quantity = existing_quantity + quantity

    post_trade_value = post_trade_quantity * price

    value_of_other_holdings = 0

    for holding in holdings:
        if holding["security_id"] != security_id:
            value_of_other_holdings += (
                holding["quantity"] * holding["market_price"]
            )

    total_portfolio_value = (
        post_trade_cash
        + post_trade_value
        + value_of_other_holdings
    )

    position_pct = post_trade_value / total_portfolio_value

    max_position_pct = portfolio["max_position_pct"]

    if position_pct > max_position_pct:
        return (
            "Needs Manual Sign-off",
            "Exceeds maximum position concentration — requires approval."
        )

    # Step 6: Approved
    return "Approved", "Trade passed all compliance checks."


def main():

    results = []

    with open("trades_test.csv", "r", newline="") as file:

        reader = csv.DictReader(file)

        for trade in reader:

            decision, reason = check_trade(trade)

            results.append({
                "portfolio_id": trade["portfolio_id"],
                "security_id": trade["security_id"],
                "action": trade["action"],
                "quantity": trade["quantity"],
                "price": trade["price"],
                "decision": decision,
                "reason": reason
            })

    # Display results
    print("\nTRADE COMPLIANCE RESULTS")
    print("=" * 100)

    for result in results:

        print(
            f"{result['portfolio_id']} | "
            f"{result['security_id']} | "
            f"{result['action']} | "
            f"{result['quantity']} | "
            f"{result['decision']} | "
            f"{result['reason']}"
        )

    # Save results to CSV
    with open("trade_results.csv", "w", newline="") as file:

        fieldnames = results[0].keys()

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("\nResults saved to trade_results.csv")


if __name__ == "__main__":
    main()

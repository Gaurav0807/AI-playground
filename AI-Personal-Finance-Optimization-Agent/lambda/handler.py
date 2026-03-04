import json
import csv
import io
import boto3
import os


GUARDRAIL_ID = os.environ.get("GUARDRAIL_ID")
GUARDRAIL_VERSION = os.environ.get("GUARDRAIL_VERSION", "DRAFT")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def categorize(description):
    CATEGORY_KEYWORDS = {
    "Food": ["swiggy", "zomato", "dominos"],
    "Transport": ["uber", "ola"],
    "Shopping": ["amazon", "flipkart"],
    "Subscription": ["netflix", "prime"]
    }

    description = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in description for word in keywords):
            return category

    if "salary" in description:
        return "Income"

    return "Other"

def get_ai_insights(financial_summary, transactions):

    prompt = f"""
    Analyze the following financial transactions and summary.

    Transactions:
    {transactions}

    Financial Summary:
    {json.dumps(financial_summary, indent=2)}

    Provide:
    - spending analysis
    - possible financial risks
    - suggestions to optimize spending
    - estimated monthly savings
    """

    converse_params = {
        "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 1000,
            "temperature": 0.7
        }
    }

    if GUARDRAIL_ID:
        converse_params["guardrailConfig"] = {
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION
        }

    response = bedrock.converse(**converse_params)

    return response["output"]["message"]["content"][0]["text"]


def handler(event, context):

    try:

        body = json.loads(event["body"])
        csv_content = body.get("csv_data")

        if not csv_content:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "csv_data missing"})
            }


        csv_reader = csv.DictReader(io.StringIO(csv_content))

        total_income = 0
        total_expense = 0
        category_totals = {}
        transactions_list = []

        for row in csv_reader:
            amount = float(row["amount"])
            description = row["description"]
            category = categorize(description)

            transactions_list.append({
                "date": row.get("date", ""),
                "description": description,
                "amount": amount,
                "category": category
            })

            if amount > 0:
                total_income += amount
            else:
                total_expense += abs(amount)

            category_totals[category] = (
                category_totals.get(category, 0) + abs(amount)
            )

        net_balance = total_income - total_expense

        financial_summary = {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "category_breakdown": category_totals
        }

        print("Financial summary:", financial_summary)
        print("Using Guardrail:", GUARDRAIL_ID)
        print("GUARDRAIL_VERSION:", GUARDRAIL_VERSION)

        ai_advice = get_ai_insights(financial_summary, json.dumps(transactions_list, indent=2))
        

        print("AI Advice:", ai_advice)

        response = {
            "financial_summary": financial_summary,
            "ai_advice": ai_advice
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response)
        }

    except Exception as e:
        print("Error occurred:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
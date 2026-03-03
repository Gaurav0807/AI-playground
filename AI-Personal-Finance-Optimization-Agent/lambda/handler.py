import json
import csv
import io
import boto3

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

def get_ai_insights(financial_summary):

    prompt = f"""
    You are a professional personal financial advisor.

    Here is the user  financial summary:

    {json.dumps(financial_summary, indent=2)}

    Please provide:
    1. Spending analysis
    2. Risk areas
    3. Specific optimization suggestions
    4. Estimated possible monthly savings

    Keep response concise and practical.
    """

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 200
        })
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

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

        for row in csv_reader:
            amount = float(row["amount"])
            description = row["description"]
            category = categorize(description)

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

        ai_advice = get_ai_insights(financial_summary)

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
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
import requests
from textblob import TextBlob
import csv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# Replace with your Google Places API Key
API_KEY = "API KEY"

# Function to search for place details
def get_place_details(place_name):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": place_name,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": API_KEY,
    }
    response = requests.get(url, params=params)
    result = response.json()
    if result["status"] == "OK":
        return result["candidates"][0]["place_id"]
    else:
        print("Error fetching place ID:", result["status"])
        return None

# Function to fetch reviews
def get_reviews(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "reviews",
        "key": API_KEY,
    }
    response = requests.get(url, params=params)
    result = response.json()
    if result["status"] == "OK":
        return result.get("result", {}).get("reviews", [])
    else:
        print("Error fetching reviews:", result["status"])
        return []

# # Sentiment analysis function
# def analyze_sentiment(review):
#     analysis = TextBlob(review)
#     sentiment_score = analysis.sentiment.polarity
#     if sentiment_score > 0:
#         return "positive"
#     elif sentiment_score < 0:
#         return "negative"
#     else:
#         return "neutral"

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(review):
    scores = analyzer.polarity_scores(review)
    compound_score = scores["compound"]
    
    if compound_score > 0.05:  # Positive sentiment
        return "positive"
    elif compound_score < -0.05:  # Negative sentiment
        return "negative"
    else:  # Neutral sentiment
        return "neutral"

# Main function
def main():
    place_name = input("Enter the name of the place: ")
    place_id = get_place_details(place_name)

    if not place_id:
        print("Could not fetch details for the given place.")
        return

    reviews = get_reviews(place_id)

    if not reviews:
        print("No reviews found for the given place.")
        return

    positive_reviews = []
    negative_reviews = []
    neutral_reviews = []
    total_rating = 0

    for review in reviews:
        text = review.get("text", "")
        rating = review.get("rating", 0)
        total_rating += rating
        sentiment = analyze_sentiment(text)

        if sentiment == "positive":
            positive_reviews.append((text, rating))
        elif sentiment == "negative":
            negative_reviews.append((text, rating))
        else:
            neutral_reviews.append((text, rating))

    # Calculate overall rating
    review_count = len(reviews)
    if review_count > 0:
        overall_rating = total_rating / review_count
    else:
        print("No ratings available.")
        return

    # Write the data to a .csv file
    output_file = f"{place_name.replace(' ', '_')}_reviews.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write section title for reviews
        writer.writerow(["Reviews"])
        writer.writerow(["Review Text", "Rating", "Sentiment"])

        # Write review details for each sentiment category
        if positive_reviews:
            writer.writerow([])  # Blank line
            writer.writerow(["Positive Reviews"])
            for review in positive_reviews:
                writer.writerow([review[0], review[1], "Positive"])

        if negative_reviews:
            writer.writerow([])  # Blank line
            writer.writerow(["Negative Reviews"])
            for review in negative_reviews:
                writer.writerow([review[0], review[1], "Negative"])

        if neutral_reviews:
            writer.writerow([])  # Blank line
            writer.writerow(["Neutral Reviews"])
            for review in neutral_reviews:
                writer.writerow([review[0], review[1], "Neutral"])

        # Write a blank row for separation
        writer.writerow([])
        writer.writerow(["Overall Summary"])
        writer.writerow(["Total Reviews", review_count])
        writer.writerow(["Overall Rating", f"{overall_rating:.2f}"])
        writer.writerow(["Positive Reviews", len(positive_reviews)])
        writer.writerow(["Negative Reviews", len(negative_reviews)])
        writer.writerow(["Neutral Reviews", len(neutral_reviews)])

    print(f"Data saved to {output_file}")


if __name__ == "__main__":
    main()
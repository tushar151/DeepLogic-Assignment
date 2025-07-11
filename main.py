from flask import Flask, jsonify
import re
import json

app = Flask(__name__)

@app.route('/getTimeStories', methods=['GET'])
def get_time_stories():
    try:
        with open("world.html", "r", encoding="utf-8") as f:
            html = f.read()
        pattern = r'self\.__next_f\.push\(\[1,"(.*?)"\]\)'
        matches = re.findall(pattern, html)

        if not matches:
            return jsonify({"error": "No data blocks found"}), 500

        def extract_posts(obj):
            """Recursively search for 'posts' key in nested dicts/lists."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "posts" and isinstance(v, list):
                        return v
                    result = extract_posts(v)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = extract_posts(item)
                    if result:
                        return result
            return None

        stories = []

        for match in matches:
            try:
                decoded = match.encode('utf-8').decode('unicode_escape')
                parsed = json.loads(decoded)

                posts = extract_posts(parsed)
                if posts:
                    for post in posts:
                        title = post.get("title")
                        path = post.get("path")
                        if title and path:
                            stories.append({
                                "title": title.strip(),
                                "link": f"https://time.com{path}"
                            })
                        if len(stories) >= 6:
                            break
                if len(stories) >= 6:
                    break
            except:
                continue

        if not stories:
            return jsonify({"error": "No valid stories found"}), 500

        return jsonify(stories)

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

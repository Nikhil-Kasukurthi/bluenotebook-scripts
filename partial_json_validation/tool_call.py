import base64
from io import BytesIO
import anthropic
import requests
from PIL import Image
import time

from pydantic_core import from_json

from data_models import Recipie

def validate_partial_json(streamed_text: str):
    if streamed_text != "":
        validated_dict = from_json(streamed_text, allow_partial=True)
        recipie = Recipie.model_validate(validated_dict)
        return recipie
    return None

def download_image_from_url(url: str) -> Image.Image:
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def validate_stream(stream, time_between_checks = 0.003):
    streamed_text = ""

    start_time = time.time()
    last_check = time.time()

    # This is the stream from anthropic
    for response in stream._raw_stream:
        if response.type == "content_block_start":
            continue
        if response.type == "content_block_delta":
            streamed_text += response.delta.partial_json

        elapsed_time = time.time() - start_time
        last_check_time = time.time() - last_check
        # check if it's been time between checks since last check
        if last_check_time >= time_between_checks:
            last_check = time.time()
            validated_json = validate_partial_json(streamed_text)
            if validated_json is not None:
                yield validated_json
    validated_json = validate_partial_json(streamed_text)
    yield validated_json

def main():
    client = anthropic.Anthropic()
    image = download_image_from_url(
        "https://bluenotebook.io/posts/streaming-fuction-calling/rasam_recipie.jpg"
    )
    # save image to jpge format at 85% quality to bytes
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    image1_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    with client.messages.stream(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        tools=[
            {
                "name": "parse_recipie",
                "description": "Parse the recipie from images into structured data",
                "input_schema": Recipie.model_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": "parse_recipie"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Catalogue this recipie"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image1_data,
                        },
                    },
                ],
            }
        ],
    ) as stream:
        for validated_json in validate_stream(stream):
            yield validated_json

if __name__ == "__main__":
    iterator = main()
    for i in iterator:
        print(i)

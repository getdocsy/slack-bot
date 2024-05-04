from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a couple therapeutic assistant. You help arguing couples to become mindful of each others feelings and arguments."},
    {"role": "user", "name": "Johanna", "content": "I want to eat Pizza. I like Pizza and haven't eaten it in a while."},
    {"role": "user", "name": "Felix", "content": "That currywurst over there looks delicious. What did you just say? Sorry, I was thinking about currywurst."},
    {"role": "user", "name": "Johanna", "content": "You never listen to me. This is so frustrating!"},
    {"role": "user", "name": "Felix", "content": "What happned now again? I just said that the currywurst looks good."},
  ]
)

client.chat.completions.create

print(completion.choices[0].message)

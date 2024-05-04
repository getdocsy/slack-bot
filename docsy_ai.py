import logging
logger = logging.getLogger(__name__)

from openai import OpenAI

prompt =      [
        {"role": "system", "content": "You are my friendly AI coworker. " +
         "Your help our company by writing public documentation that answers the questions people have about our product." +
         "As input, you will receive chat conversations where someone asks a questions and someone answers the question and a markdown file that should answer the question but doesn't yet." +
         "Exclusively write about what is in the product today. Do not include anything about features that are not implemented yet. Use active voice and present tense."},
      ] 


def get_suggestion(messages):
    client = OpenAI()
    
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages= prompt +[{"role": "user", "name": message[0], "content": message[1]} for message in messages]
    )
    
    client.chat.completions.create
    return completion.choices[0].message.content

def main():
    logging.basicConfig(level=logging.INFO)

    kraken_api_messages = [('U068ZT2R7DG', "Where do I find the Kraken API docs :grimacing: I tried finding them via [https://docs.meshcloud.io](https://docs.meshcloud.io/) but couldn't ..."),
                ('U068ZT2R7DG', "https://kraken.dev.meshcloud.io/docs/index.html. It's a bit hidden there also exist a ticket for it https://app.clickup.com/t/86bwhj5m0"),
                ('U068ZT2R7DG', 'thanks'), 
                ('U068T9HGHAA', 'Hey there <@U068ZT2R7DG>! You learned something new today. Do you want me to come up with a Knowledge base entry for that?'), 
                ('U068T9HGHAA', "All right, <@U068ZT2R7DG>. I'll get back to you with a suggestion")]
    print(get_suggestion(kraken_api_messages))

if __name__ == '__main__':
    main()

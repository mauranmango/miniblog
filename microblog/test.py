# from microblog.models import User
# from microblog import db
#
#
#
# # # db.create_all()
# user = User(username='susan', email="susan@example.com")
# user.set_password('susan')
# db.session.add(user)
# db.session.commit()
# from microblog import app, mail
# from flask_mail import Message
#
# msg = Message("test subject", sender=app.config['ADMINS'][0], recipients=['mauran.mango@yahoo.com'])
# msg.body = 'text body'
# msg.html = '<h1>Testing Html body</h1>'
# mail.send(msg)

# import jwt
#
# # Dictionaryn e enkripton me algoritmin 256 dhe me key qe kemi percaktuar qe duhet te jete shume sekret
# # Nje feature tjeter qe kane token eshte qe kane date skadence
# # token = jwt.encode({'a': 'b'}, "my-secret", algorithm='HS256')
# # print(token)
# #
# #
# # Ne kete menyre dekodojme informacionin qe koduam. Mund te kemi shume algoritme qe suportojme prandaj e percaktojme si liste
# # print(jwt.decode(token, 'my-secret', algorithms=['HS256']))
#
#
# import requests, uuid, json
# from microblog import app
#
# # Add your key and endpoint
# key = '7156f705b5f94900882b814df71bc016'
# endpoint = "https://api.cognitive.microsofttranslator.com"
#
# # location, also known as region.
# # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
#
# path = '/translate'
# constructed_url = endpoint + path
#
# params = {
#     'api-version': '3.0',
#     'from': 'en',
#     'to': ['sq']
# }
#
# headers = {
#     'Ocp-Apim-Subscription-Key': key,
#     # location required if you're using a multi-service or regional (not global) resource.
#     'Ocp-Apim-Subscription-Region': 'germanywestcentral',
#     'Content-type': 'application/json',
#     'X-ClientTraceId': str(uuid.uuid4())
# }
#
# # You can pass more than one object in body.
# body = [{
#     'text': 'I would really like to drive your car around the block a few times! Hi dude!'
# }]
#
# request = requests.post(constructed_url, params=params, headers=headers, json=body)
# response = request.json()
# print(response[0]['translations'][0]['text'])
#
# # print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))

from microblog.models import Post

posts = Post.query.filter_by(user_id=4)

for post in posts:
    print(post.body)
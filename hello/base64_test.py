import base64

# 对字符串进行Base64编码
string = 'Hello, World!'
# 将字符串转换为字节串
bytes_string = string.encode('utf-8')
print(bytes_string)
# 进行Base64编码
base64_string = base64.b64encode(bytes_string)
print(type(base64_string))
# 将字节串转换为字符串
encoded_string = base64_string.decode('utf-8')

print(type(encoded_string))

# 对Base64编码的字符串进行解码
decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
print(type(decoded_bytes))
# 将字节串转换为字符串
decoded_string = decoded_bytes.decode('utf-8')

print(decoded_string)

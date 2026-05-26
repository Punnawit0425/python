while True:
    text = input("Enter a string (or 'quit' to exit): ")
    if text == "quit":
        break
    def is_palindrome(s):
        s = s.lower()
        return s == s[::-1]
    if is_palindrome(text):
        print("The string is a palindrome")
    else:
        print("The string is not a palindrome")
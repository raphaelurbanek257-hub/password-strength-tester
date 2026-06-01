#!/usr/bin/env python3
import re
import sys
import math
import hashlib
import requests
from datetime import datetime

COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password1", "admin",
    "letmein", "welcome", "monkey", "dragon", "master", "sunshine", "iloveyou",
    "trustno1", "123123", "football", "baseball", "whatever", "shadow", "ninja",
    "mustang", "michael", "jordan", "harley", "ranger", "thomas", "jennifer",
    "charles", "thunder", "ferrari", "mercedes", "bitcoin", "coffee", "internet",
    "orange", "banana", "butterfly", "flower", "password123", "admin123", "qwerty123"
}

def check_entropy(password):
    charset_size = 0
    if re.search(r'[a-z]', password):
        charset_size += 26
    if re.search(r'[A-Z]', password):
        charset_size += 26
    if re.search(r'[0-9]', password):
        charset_size += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        charset_size += 33
    
    if charset_size == 0:
        return 0
    return len(password) * math.log2(charset_size)

def check_common(password):
    return password.lower() in COMMON_PASSWORDS

def check_patterns(password):
    issues = []
    sequences = ["123456", "qwerty", "asdfgh", "zxcvbn", "abcd", "098765"]
    for seq in sequences:
        if seq in password.lower():
            issues.append(f"Sequential pattern: '{seq}'")
    
    if re.search(r'(.)\1{2,}', password):
        issues.append("Repeated characters (e.g., 'aaa')")
    
    keyboard_patterns = ["qwerty", "asdf", "zxcv", "1234", "qwer"]
    for pattern in keyboard_patterns:
        if pattern in password.lower():
            issues.append(f"Keyboard pattern: '{pattern}'")
    
    years = [str(year) for year in range(1950, 2030)]
    for year in years:
        if year in password:
            issues.append(f"Contains year: '{year}'")
    
    return issues

def check_dictionary_words(password):
    common_words = {
        "admin", "user", "login", "pass", "secret", "private", "public",
        "hello", "world", "test", "demo", "example", "sample", "default",
        "root", "system", "network", "server", "client", "database"
    }
    found = []
    password_lower = password.lower()
    for word in common_words:
        if word in password_lower:
            found.append(word)
    return found

def check_length(password):
    length = len(password)
    if length < 8:
        return "Too short (<8 chars)", 0
    elif length < 12:
        return "Moderate", 1
    elif length < 16:
        return "Good", 2
    else:
        return "Excellent", 3

def check_complexity(password):
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
    
    score = sum([has_lower, has_upper, has_digit, has_special])
    types = []
    if has_lower: types.append("lowercase")
    if has_upper: types.append("uppercase")
    if has_digit: types.append("numbers")
    if has_special: types.append("special")
    
    return score, types

def estimate_crack_time(entropy):
    guesses_per_second = 1000000000
    if entropy <= 0:
        return "Unknown"
    guesses = 2 ** entropy
    seconds = guesses / guesses_per_second
    
    if seconds < 60:
        return "Less than 1 minute"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 315360000:
        return f"{int(seconds / 31536000)} years"
    else:
        return f"Centuries ({int(seconds / 31536000)} years)"

def check_breach(password):
    try:
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.split(':')[0] == suffix:
                    return int(line.split(':')[1])
        return 0
    except:
        return -1

def get_suggestions(password, entropy, complexity_score):
    suggestions = []
    if entropy < 40:
        suggestions.append("Make password longer (12+ characters)")
    if not re.search(r'[A-Z]', password):
        suggestions.append("Add uppercase letters")
    if not re.search(r'[0-9]', password):
        suggestions.append("Add numbers")
    if not re.search(r'[^a-zA-Z0-9]', password):
        suggestions.append("Add special characters (!@#$%^&*)")
    if check_common(password):
        suggestions.append("Avoid common passwords")
    dict_words = check_dictionary_words(password)
    if dict_words:
        suggestions.append(f"Avoid dictionary words: {', '.join(dict_words)}")
    return suggestions

def get_rating(complexity_score, entropy, length_score, password):
    total = complexity_score + length_score
    if entropy >= 60 and total >= 5 and not check_common(password):
        return "EXCELLENT"
    elif entropy >= 50 and total >= 4:
        return "STRONG"
    elif entropy >= 35 and total >= 3:
        return "MODERATE"
    elif entropy >= 20:
        return "WEAK"
    else:
        return "VERY WEAK"

def main():
    print("Password Strength Tester v1.0")
    print("="*50)
    
    while True:
        password = input("\nEnter password to test (or 'quit'): ")
        
        if password.lower() in ['quit', 'exit', 'q']:
            print("Goodbye.")
            sys.exit(0)
        
        if len(password) == 0:
            print("Please enter a password.")
            continue
        
        print("\nAnalyzing...\n")
        
        entropy = check_entropy(password)
        common = check_common(password)
        patterns = check_patterns(password)
        dict_words = check_dictionary_words(password)
        length_text, length_score = check_length(password)
        complexity_score, types = check_complexity(password)
        crack_time = estimate_crack_time(entropy)
        breach_count = check_breach(password)
        suggestions = get_suggestions(password, entropy, complexity_score)
        rating = get_rating(complexity_score, entropy, length_score, password)
        
        print("="*50)
        print(f"Password: {password}")
        print(f"Length: {len(password)} chars")
        print(f"Entropy: {entropy:.1f} bits")
        print(f"Complexity: {complexity_score}/4 ({', '.join(types) if types else 'none'})")
        print(f"Length rating: {length_text}")
        print(f"Crack time: {crack_time}")
        print("-"*50)
        
        if common:
            print("[!] Common password: YES")
        else:
            print("[+] Common password: No")
        
        if dict_words:
            print(f"[!] Dictionary words: {', '.join(dict_words)}")
        else:
            print("[+] Dictionary words: None")
        
        if patterns:
            for p in patterns:
                print(f"[!] {p}")
        else:
            print("[+] No patterns detected")
        
        if breach_count == -1:
            print("[?] Breach check: Offline")
        elif breach_count > 0:
            print(f"[!] Found in {breach_count} data breaches!")
        else:
            print("[+] Not found in known breaches")
        
        print("-"*50)
        print(f"Final rating: {rating}")
        
        if suggestions:
            print("\nSuggestions:")
            for i, sug in enumerate(suggestions, 1):
                print(f"  {i}. {sug}")
        
        print("="*50)
        
        again = input("\nTest another? (y/n): ")
        if again.lower() != 'y':
            print("Goodbye.")
            break

if __name__ == "__main__":
    main()
       
  

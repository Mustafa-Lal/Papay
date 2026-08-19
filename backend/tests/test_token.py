from app.security.tokens import generate_token, hash_token


def main() -> None:
    token = generate_token()
    token_hash = hash_token(token)

    print("Token:")
    print(token)

    print("\nToken hash:")
    print(token_hash)

    print("\nToken length:", len(token))
    print("Hash length:", len(token_hash))


if __name__ == "__main__":
    main()

# З великої літери потрібно писати слова довжиною 4 чи більше літер.
import pymorphy2
import tokenize_uk

str_input = "Карантин обвалив гривню. Чи буде долар по 30 і як довго триватиме паніка"

#morph= pymorphy2.MorphAnalyzer(lang='uk')
tokenized_str = tokenize_uk.tokenize_words(str_input)
print(tokenized_str)
for i in range(len(tokenized_str)):
    if len(tokenized_str[i])>3:
        tokenized_str[i] = tokenized_str[i].capitalize()


print(tokenized_str)


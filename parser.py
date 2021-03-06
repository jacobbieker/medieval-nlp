__author__ = 'Jacob Bieker'
import os, sys
import nltk, re, pprint
from nltk.corpus import stopwords
from nltk import word_tokenize
from multiprocessing import Pool
#nltk.download()
from wordcloud import WordCloud
import numpy as np
from PIL import Image

def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def findtags(tag_prefix, tagged_text):
    cfd = nltk.ConditionalFreqDist((tag, word) for (word, tag) in tagged_text
                                   if tag.startswith(tag_prefix))
    return dict((tag, cfd[tag].most_common(10)) for tag in cfd.conditions())


def find_multiple_tags(tag_prefix_list, tagged_text):
    big_tagdict = []
    for item in tag_prefix_list:
        tagdict = findtags(item, tagged_text)
        for tag in sorted(tagdict):
            print(tag, tagdict[tag])
        big_tagdict.append(tagdict)
    return big_tagdict


def counting_words(word_list, tagged_text, nltk_text, nltk_processed):
    for small_list in word_list:
        word_count = 0
        for word in small_list:
            word_count += nltk_text.lower().count(word) / len(tagged_text)
            #print("Word: " + word)
            #print(nltk_processed.concordance(word))
            #print("Similar Words:")
            #print(nltk_processed.similar(word))
        print("Similar Words To: " + str(small_list[0]))
        print("Ratio to full text: " + str(word_count * 100))


def wordcloud_make(text, discipline, image_name):
    alice_mask = np.array(Image.open(os.path.join(image_name)))
    wc = WordCloud(background_color="white", mask=alice_mask)

    # generate word cloud
    wc.generate(text)

    # store to file
    wc.to_file(os.path.join(str(discipline + ".png")))

dict_of_texts = {}
dict_of_freq = {}
total_words = 0
total_sentences = 0

#sys.stdout = open("print-outfile.txt", "w")
with open("outfile.txt", "w") as output:
    for filename in os.listdir(os.path.join("primary-sources")):
        with open(os.path.join("primary-sources", filename)) as nltk_text:
            print(filename)
            raw_data = nltk_text.read()
            mod_raw = []
            for character in raw_data:
                if character.isalnum() or character == " " or character == "\n" or character == "-":
                    mod_raw.append(character)

            new_raw = ""
            new_raw = new_raw.join(mod_raw)
            if filename == "William of Malmesbury's Chronicle of the Kings of England.txt":
                wordcloud_make(new_raw, "malmesbury", "kings-of-england-pic.png")
            elif filename == "Master Wace's Chronicle of the Norman Conquest.txt":
                wordcloud_make(new_raw, "wace", "wace-pic.png")
            elif filename == "Full The ecclesastical history of England.txt":
                wordcloud_make(new_raw, "vitalis", "orderic-vitalis-pic.png")
            elif filename == "Full The annals of Roger de Hoveden.txt":
                wordcloud_make(new_raw, "roger", "roger-pic.png")
            elif filename == "Florence of Worcester's Chroncile.txt":
                wordcloud_make(new_raw, "florence", "john-pic.png")
            elif filename == "Chronicle of Henry Huntingdon.txt":
                wordcloud_make(new_raw, "henry", "huntingdon-pic.png")
            elif filename == "Anglo-Saxon Chronicle.txt":
                wordcloud_make(new_raw, "saxon", "anglo-saxon-pic.png")
            elif filename == "Hereward of Wake.txt":
                wordcloud_make(new_raw, "monmouth", "monmouth-pic.png")
            nltk_processed = nltk.Text(raw_data)
            print(nltk_processed.collocations())
            # After removing stopwords and punctuation do analysis again
            processed_2 = nltk.sent_tokenize(raw_data)
            processed_1 = nltk.word_tokenize(raw_data)
            processed = nltk.pos_tag(processed_1)
            #text = nltk.Text(ie_preprocess(raw_data))
            #text_lower = nltk.Text(ie_preprocess([word.lower() for word in raw_data]))
            output.write(filename + "\n")
            output.write("Num Characters: " + str(len(raw_data)) + "\n")
            output.write("Num Words: " + str(len(processed)) + "\n")
            total_words += len(processed)
            output.write("Num Sentences: " + str(len(processed_2)) + "\n")
            total_sentences += len(processed_2)
            tag_fd = nltk.FreqDist(tag for (word, tag) in processed)
            fd = nltk.FreqDist(word for (word, tag) in processed)
            dict_of_freq[filename] = tag_fd
            dict_of_texts[filename] = processed
            output.write("\n\n")
            wanted_tags = ["NN", "JJ", "VB"]
            tag_list = find_multiple_tags(wanted_tags, processed)
            interesting_words = [["king", "kings",],
                                 ["queen", "queens"],
                                 ["army", "military", "battle", "fight", "troops", "troop", "armies"],
                                 ["church", "churches", "bishop", "bishops", "archbishop", "archbishops",
                                  "priest", "priests", "clergy", "bible", "holy", "god"],
                                 ["title", "earl", "king", "earls", "kings", "duke", "dukes", "regent", "regents",
                                  "knight", "knights", "noble", "nobles", "lord", "lords"]]
            counting_words(interesting_words, processed, raw_data, nltk_processed)
            # N-grams
            ngrams = nltk.ngrams(processed, n=5)
            fdist = nltk.FreqDist(ngrams)
            keys = fdist.keys()
            print("Ngrams")
            print(fdist.most_common(20))
            print("\n\n")


    output.write("Total words: " + str(total_words))
    output.write("Total Sentences: " + str(total_sentences))

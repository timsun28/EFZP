#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

import re
import string
import Internationalization

def parse(email_text, lang='english', remove_quoted_statements=True):
    email_text = email_text.strip()
    email_text = strip_automated_notation(email_text)    
    if remove_quoted_statements:
        pattern = """(?P<quoted_statement>".*?")"""
        matches = re.findall(pattern, email_text, re.IGNORECASE + re.DOTALL)
        for m in matches:
            email_text = email_text.replace(m, '"[quote]"')
    result = {
        "salutation": get_salutation(email_text, lang),
        "body": get_body(email_text, lang),
        "signature": get_signature(email_text, lang),
        "reply_text": get_reply_text(email_text)
    }
    return result

#automated_notation could be any labels or sections in the email giving special notation for
#human readers of the email text. For example, email_text may start with "A message from your customer:"
def strip_automated_notation(email_text):
    #Use a paramater name email_text to indicate text in the actual email message
    notations = [
                 "Hi, there has been a new enquiry from\..*?Enquiry:(?P<email_message>.*)",
                 ]
    for n in notations:
        groups = re.match(n, email_text, re.IGNORECASE + re.DOTALL)
        if not groups is None:
            if groups.groupdict().has_key("email_message"):
                email_text = groups.groupdict()["email_message"]
    
    return email_text
    

def get_reply_text(email_text):
    #Notes on regex
    #Search for classic prefix from GMail and other mail clients "On May 16, 2011, Dave wrote:"
    #Search for prefix from outlook clients From: Some Person [some.person@domain.tld]
    #Search for prefix from outlook clients when used for sending to recipients in the same domain From: Some Person\nSent: 16/05/2011 22:42\nTo: Some Other Person
    #Search for prefix when message has been forwarded
    #Search for From: <email@domain.tld>\nTo: <email@domain.tld>\nDate:<email@domain.tld
    #Search for From:, To:, Sent:
    #Some clients use -*Original Message-*
    pattern = "(?P<reply_text>" + \
        "On ([a-zA-Z0-9, :/<>@\.\"\[\]]* wrote:.*)|" + \
        "From: [\w@ \.]* \[mailto:[\w\.]*@[\w\.]*\].*|" + \
        "From: [\w@ \.]*(\n|\r\n)+Sent: [\*\w@ \.,:/]*(\n|\r\n)+To:.*(\n|\r\n)+.*|" + \
        "[- ]*Forwarded by [\w@ \.,:/]*.*|" + \
        "From: [\w@ \.<>\-]*(\n|\r\n)To: [\w@ \.<>\-]*(\n|\r\n)Date: [\w@ \.<>\-:,]*\n.*|" + \
        "From: [\w@ \.<>\-]*(\n|\r\n)To: [\w@ \.<>\-]*(\n|\r\n)Sent: [\*\w@ \.,:/]*(\n|\r\n).*|" + \
        "From: [\w@ \.<>\-]*(\n|\r\n)To: [\w@ \.<>\-]*(\n|\r\n)Subject:.*|" + \
        "(-| )*Original Message(-| )*.*)"
    groups = re.search(pattern, email_text, re.IGNORECASE + re.DOTALL)
    reply_text = None
    if not groups is None:
        if groups.groupdict().has_key("reply_text"):
            reply_text = groups.groupdict()["reply_text"]
    return reply_text
    

def get_signature(email_text, lang):
    
    #try not to have the signature be the very start of the message if we can avoid it
    salutation = get_salutation(email_text, lang)
    if salutation: email_text = email_text[len(salutation):]
    
    #note - these openinged statements *must* be in lower case for 
    #sig within sig searching to work later in this func
    sig_opening_statements = Internationalization.get_signature(lang)
    pattern = "(?P<signature>(" + string.joinfields(sig_opening_statements, "|") + ")(.)*)"
    groups = re.search(pattern, email_text, re.IGNORECASE + re.DOTALL)
    signature = None
    if groups:
        if groups.groupdict().has_key("signature"):
            signature = groups.groupdict()["signature"]
            reply_text = get_reply_text(email_text[email_text.find(signature):])
            if reply_text: signature = signature.replace(reply_text, "")
            print(signature)

            #search for a sig within current sig to lessen chance of accidentally stealing words from body
            tmp_sig = signature
            for s in sig_opening_statements:
                if tmp_sig.lower().find(s) == 0:
                    tmp_sig = tmp_sig[len(s):]
            groups = re.search(pattern, tmp_sig, re.IGNORECASE + re.DOTALL)
            if groups: signature = groups.groupdict()["signature"]

    #if no standard formatting has been provided (e.g. Regards, <name>),
    #try a probabilistic approach by looking for phone numbers, names etc. to derive sig    
    if not signature:
        #body_without_sig = get_body(email_text, check_signature=False)
        pass
    
    #check to see if the entire body of the message has been 'stolen' by the signature. If so, return no sig so body can have it.
    body_without_sig = get_body(email_text, lang, check_signature=False)
    if signature==body_without_sig: signature = None
    
    return signature

#todo: complete this out (I bit off a bit more than I could chew with this function. Will probably take a bunch of basian stuff
def is_word_likely_in_signature(word, text_before="", text_after=""):
    #Does it look like a phone number?
    
    #is it capitalized?
    if word[:1] in string.ascii_uppercase and word[1:2] in string.ascii_lowercase: return True
    
    return
    
#check_<zone> args provided so that other functions can call get_body without causing infinite recursion
def get_body(email_text, lang, check_salutation=True, check_signature=True, check_reply_text=True):
    
    if check_salutation:
        sal = get_salutation(email_text, lang)
        if sal: email_text = email_text[len(sal):]
    
    if check_signature:
        sig = get_signature(email_text, lang)
        if sig: email_text = email_text[:email_text.find(sig)]
    
    if check_reply_text:
        reply_text = get_reply_text(email_text)
        if reply_text: email_text = email_text[:email_text.find(reply_text)]
            
    return email_text

def get_salutation(email_text, lang):
    #remove reply text fist (e.g. Thanks\nFrom: email@domain.tld causes salutation to consume start of reply_text
    reply_text = get_reply_text(email_text)
    if reply_text: email_text = email_text[:email_text.find(reply_text)]
    #Notes on regex:
    #Max of 5 words succeeding first Hi/To etc, otherwise is probably an entire sentence
    salutation_opening_statements = Internationalization.get_salutations(lang)
    pattern = "\s*(?P<salutation>(" + string.joinfields(salutation_opening_statements, "|") + ")+(\s*\w*)(\s*\w*)(\s*\w*)(\s*\w*)(\s*\w*)[\.,\xe2:]+\s*)"
    groups = re.match(pattern, email_text, re.IGNORECASE)
    print(groups)
    salutation = None
    if not groups is None:
        if groups.groupdict().has_key("salutation"):
            salutation = groups.groupdict()["salutation"]
    return salutation
    
test = get_signature('Beste, Momenteel schrijf ik mijn scriptie over de factoren die van invloed zijn op de inkomensongelijkheid in Nederland. Ik kan op de website van CBS slechts gegevens vinden over de Gini-coefficient en de verschillende inkomensaandelen tussen 2000 en 2014. Ik heb echter een artikel gevonden waar een grafiek is gemaakt van de gegevens vanaf 1990.Uit de betreffende grafiek zijn de gegevens helaas niet precies genoeg af te lezen. Mijn vraag is nu waar ik de gegevens over inkomensongelijkheid en inkomensaandelen over de periode van 1990 - 2016 kan vinden. Alvast bedankt. Vriendelijke groet,Hannah Elenbaas', 'dutch')
print(test)
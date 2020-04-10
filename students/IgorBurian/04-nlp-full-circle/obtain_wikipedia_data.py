import wikipedia
import json
import re
import time
                    
with open('physicists.json', 'r') as json_file:
    physicists = [p['name'] for p in json.load(json_file)]
  
    with open('wikipedia.txt', 'w') as out:
        with open('failures.txt', 'w') as failures:
    
            for p in physicists:
                try:
                    print(p)
                    page = wikipedia.page(p)
                    out.write('#### {} ####\n'.format(p))
                    out.write(page.content + '\n\n')
                    time.sleep(1)
                except Exception as e:
                    print('Error occured during "{}" page load'.format(p))
                    print(e)
                    failures.write([p] + '\n')
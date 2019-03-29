Documentation for the Archive Sharpshooter (ASS) program

1. Definition

Archiving SharpShooter (ASS) is a Python2 script that helps automate archiving websites with dynamically loaded content (usually comments). Modern comment plugins, such as Facebook, Disqus, require the user to click on "Load comments" or "Load more comments" buttons in order to show the content. This makes archiving such websites with simple tools like wget impossible, or at least very difficult.

Having some software running in the background that, acting as a proxy, stores HTTP traffic in archive files, a user can completely archive any website by manually clicking through it. The purpose of ASS is to automate this clicking-through process.


2. Prerequisites

In order for ASS to run, you need a recent GNU/Linux environment, with python, python-pip and scrot packages installed. Then, with Python's own package manager (pip), you need to install the opencv-python-headless and the pyautogui packages.

# apt-get install python python-pip scrot
# pip install opencv-python-headless pyautogui

If your purpose is archiving, you need a program in the background that stores HTTP traffic in archive files. I recommend using the warcprox utility, developed by the Internet Archive itself. More info on Warcprox: https://github.com/internetarchive/warcprox

# pip install warcprox

You also need a regular graphical web browser. Any decent recent browser will make it, like Firefox or Chroumium.

Finally, clone this repository.


3. Customizing the script

The first part of the script defines methods that do specific tasks. Normally, you don't need to edit these, just using them by calling them.

The predefined methods are the following:

find(template, threshold)

Looks for an image in the current content of the screen. If it finds that, returns its coordinates. If not, it returns a special value, None.
You don't normally need to call this method yourself, it is called by other methods.

wait_till(image, threshold, appear, timeout)

This method takes a screenshot in every few seconds (default is 3, you can change this with the delay variable in the beginning of the method definition), and doesn't let the program go further in execution until the given image appears (if the appear argument is True) or disappears (if the appear argument is False). You can specify a timeout – if this number of seconds has elapsed, the program goes further in execution even if the image hasn't appeared/disappeared yet.

In case of timeout, the return value is None. If the appear argument is true and the image has been found, its coordinates are returned. If the appear argument is false and the image is not found (any more), the return value is 2009.

scroll_click(timeout, exit, *args)

This method takes a screenshot in every few seconds, and looks for templates (images) on the screen, each with given thresholds. These are provided as (template, threshold) pairs in *args. (More about it soon.) If one of the template is visible on the screen, the program clicks in its middle. If not, it scrolls down.

If one of the desired templates are found, the method ends with return value 1. If the timeout has elapsed, the method ends with return value -1. The method also ends if it finds a specified exit template (e.g. bottom of page), with return value 0. You need to handle each of the three exit conditions appropriately.

Example:
scroll_click(60, (bottom, 0.005), (morecomments_base, 0.011), (more_replies, 0.01))

Here, if morecomments_base is found with 0.011 threshold, or more_replies is found with 0.01 threshold, the method ends with return value 1. If bottom is found with 0.005 threshold, the method ends with return value 0. If nothing is found in 60 seconds, the method ends with return value -1.

The templates must be given in (template, threshold) pairs both in *args and exit. A template is an image representation by the cv2.imread method, created from a regular png file from the disk. (Technically, it is a Python object.) They are defined in the user data section of the code.

Example:
icon = cv2.imread('icon.png', 0)

Here, the template named icon is created from the image file named icon.png. In the program, you can refer to this image with icon, this will be the first value in the (template, threshold) pair.

The templates are searched for by the cv2 Python libary in the screenshot. It matches the template to different parts of the screen, and every time, it computes a value that tells how much the pattern differs from the given part of the screen. If 0 is computed, the template matches exactly. If 1 is computed, the template doesn't match at all. By giving the threshold, you decide under what value you consider cv2 found the template on the screen. Although it would be logical to think that if the template is on the screen, always 0 is computed, this is rarely the case, as the cv2 library won't check every possible layout, as that would take too much time, so it not always finds the perfect match. – You need to find the right threshold for each template with a trial-and-error approach. The good value is usually between 0.005 and 0.02.

The program itself

After the definition of these method, the code of the actual algorithm begins, which is a Python program, using the methods above.

Unfortunately, this repository contains code and templates for a specific website (hvg.hu, with Hungarian locale). You need to rewrite this program yourself, that is tailored for the website you want to archive.

Fortunately, you can use this state of the program as a starting point, and probably not too many things need to be changed.


4. What do you exactly need to do to create the correct suite?

i. Discover the website you want to archive. What to find, where to click, how to find out if there are no more comments.
ii. Print screen and cut out the images that need to be recognized and/or clicked (logos, labels, buttons etc.) All of them need an image file in the same directory where ass.py resides.
iii. Write the code lines that import these images to the program (in the USER DATA section). These are lines like icon = cv2.imread('icon.png', 0).
iv. Write (modify) the algorithm from the PROGRAM START line in the code.
v. Put some URLs in a text file next to the program, start a web browser, and start the program, its argument is the text file with the URLs. (E.g. ./ass.py test.txt) (You may need a chmod u+x ass.py for the first time.) While the program is running, the browser must be in the foreground.
vi. Test and correct. You'll see some debugging messages in the console. They help you determine the correct thresholds, and help you find out what happened and why.


5. Preparing Warcprox

In order to be able to save HTTP traffic, you basically need to do two things.

i. Set the proxy settings in your browser. Find the appropriate page where you can set manual proxy, the default settings are IP address 127.0.0.1 (that is, localhost), and port 8000.
ii. When you first run warcprox, it creates a <hostname>-warcprox-ca.pem certificate file. You need to add this manually to your browser, otherwise your browser will refuse to connect via HTTPS (the proxy prevents checking the website's certificate). This would be otherwise a security risk, so use it only for archiving.

Tip: If you use Firefox, set up a new profile (by starting Firefox with -p option) dedicated for archiving. (Of course, you can also use a different browser for it other than the one you use for regular web surfing.) This is desirable also because you can't surf the web if the manual proxy is set, but warcprox is not running – that is, when you are not archiving.

You should create a dedicated folder on your filesystem for warcprox, and start warcprox from that folder. There will be collected all the certificates from the websites (in a <hostname>-warcprox-ca folder), and, in a warcs folder, all the warcs created.

You are strongly recommended to start warcprox with the -z option, this way compressed (warc.gz) files are created. Uncompressed warc files take much more space, are very rare on the Internet Archive, and they cannot be simply compressed later (warc.gz files are compressed record by record).


5. Using the suite

If you have assembled and tested the suite, and configured warcprox, you can start the process of actual archiving.

Beforehand, you need to create a list of URLs that you want to archive (e.g. articles of a news site, entries of a blog etc.). This is out of the scope of this document, so let's assume you have a list of URLs in a textfile.

A deployment of the suite is as follows:

i. Open a terminal window (LXTerminal, Xterm etc.), cd to the warcprox-dedicated directory, and issue warcprox -z.
ii. Start the dedicated web browser.
iii. Open another terminal window or tab, cd into the script directory, and issue the following command: sleep 5; ./ass.py urls.txt (assuming urls.txt is the file with the URLs). Note: sleep 5 is there just to give yourself time to do the next step before the script actually starts.
iv. Switch to the browser window. You are recommended to switch to fullscreen mode (by pressing F11), this way the script needs less time to scroll through the pages. (For the time of typing the next URL, the script switches back to non-fullscreen mode.)

Now the script starts running, and it scrapes all the URLs one by one, according to the algorithm you programmed in ass.py.

Note: The script completely simulates a living person in front of the computer. It simulates keypresses and clicks. Therefore, you can't put the task in the background, you can't do anything else with the machine. Run the script only when you can leave the computer alone (e.g. at night).

For stopping the archiving, even if there are remaining URLs, do the following:

i. Switch to the terminal window running the script. The best time for this is just after a new URL has been typed in the browser's address bar, as the page probably needs a few seconds to be loaded, and the script won't press any key during that (unless you've changed this behavior).
ii. Press Ctrl+C once, or if needed, twice, until you get back to the prompt.
iii. Close the browser window. (This is necessary so that no new requests are made by the webpage or the browser while you're stopping warcprox.)
iv. Switch to the terminal window running warcprox. If text is scrolling, wait until all transactions are finished. If the window is idle, press Ctrl+C ONCE. You'll see several threads of warcprox stopping and after a few seconds you get back to the prompt.
v. You'll find one or more WARC files in the warcs directory. Their name contains a timestamp of the launch of the script, and a random identifier. After every 1 GB of compressed data, a new WARC is started, with the same prefix, with an index in the end of the filename.
vi. If you haven't archived all URLs, and want to continue later, edit the URL list file, by deleting the already archived URLs. Then, whenever you start again the above process, it continues from the next URL. (If you forget to delete already-archived URLs, archiving starts again from the first URL.)

Notes:

i. Upon a new run, warcprox doesn't append to already existing warc files, but starts a new one.
ii. warcprox keeps a database about already visited URLs, so page requisites and other repetitive stuff won't be downloaded again. If you want to get rid of this database, delete the warcprox.sqlite file.
iii. ASS keeps a record of URLs that it considered unsuccessfully archived. They are appended to the ERRORS file in the same directory where ass.py resided. What is considered unsuccessfully archived depends on the algorithm you coded. In fact, putting the failed URLs to ERRORS is also part of the code you may rewrite. By default, a URL is considered successfully archived if the bottom of the page has been reached, after not finding any (more) comments. In other cases, or if the program times out, it retries once, and if that try also fails, the URL is appended to ERRORS.

A URL can fail for several reasons. You need to check them one by one, and scroll them through manually. If it seems that the URLs errored out for some temporary problem, you can retry them by putting back their URLs to the URLs file fed with ass.py. If too many URLs end up in ERRORS, you should improve the code, the template images, or the thresholds.

Never trust this program completely: it is complicated enough, and the pattern matching is imperfect enough so that it needs close attention in the beginning. If too few URLs appear in ERRORS, be suspicious – too good to be true. (In my use cases, the rate of erronous URLs are between 1–5%.)


6. Encouraging words

It may seem a long, difficult and tedious task to set up the suite for the first time, and to write, test and fine-tune the code for your first project. However, if you once finish that, the program can archive thousands of pages without your intervention. Your well-written algorithm needs to be changed only when the page layout or some signs, logos, labels change on the website or in the comments plugin. (Pay attention to this, look at that sometimes!)

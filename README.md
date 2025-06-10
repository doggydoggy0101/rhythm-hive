# Rhythm Hive
A small python project to (ideally) auto-play Rhythm Hive.

https://github.com/user-attachments/assets/c8e401d6-06a2-4833-a31a-9bed05c6efb1

### :cherry_blossom: Set-up
Install dependencies:

```sh
pip install -r requirements.txt
```
### :video_game: Usage
First open iPhone Mirroring and Rythym Hive inside it, then run the following command:

```sh
python main.py
```

After you start a gameplay, click the `Activate` button (or press key A) to enable auto-play.
 
> Note that if you activate it outside the gameplay, it will likely quit by itself, please make sure you are already in a gameplay before activating.

I am using iPhone 16 with the speed setting set to 7.0, running of MacBook M1 Pro. If the timing feels off for you, try adjusting the speed setting or the `delay_frames=1` in `main.py` manually.

### :cat: TL;DR

The idea is to capture the game by iPhone Mirroring in real-time, detect the notes, then simulates input by mouse automation.
I started by first implementing some basic features, then later found out that **macOS does not support multiple simultaneous mouse inputs**. I guess this is a limitation that cannot be bypassed, however, feel free to open an issue or PR if you have any ideas.

**Implementation details**

The red bar represents the detection region where luminance is computed. We set a luminance threshold to determine an action and its corresponding position for input. The logic for tap (`press` then `release`) and slide (`press`, `move`, then `release`) is similar, in fact, the logic for slide can also handle tap. I have not come up with a good solution for the swipe (arrow) case yet, I currently replace `release` by `swipe up`, that is, all tap, slide, and swipe ends with `swipe up`.

As shown in the demo video, tap and slide works well, swipe works in most cases, and simultaneously pressing two places currently fails. All configuration settings can be found in `main.py`. The screen shot method is based on this project: [MapleStory Artale ExpLab](https://github.com/StephLin/maplestory-artale-explab).

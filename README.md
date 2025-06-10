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

I am using iPhone 16 with the speed setting set to 7.0. If the timing feels off for you, try adjusting the speed setting or the `delay_frames=1` in `main.py` manually.

### :cat: TL;DR

The idea is to capture the game by iPhone Mirroring in real-time, detect the notes, then simulates input by mouse automation.
I started by first implementing some basic features, then later found out that **macOS does not support multiple simultaneous mouse inputs**, which might be a limitation that cannot be bypassed. I guess this approach might not be feasible, however, feel free to open an issue / PR if you have any ideas.

In addition, swipe (arrow) actions have not been implemented. In the demo video, swipe actions and simultaneously pressing two places currently fail.

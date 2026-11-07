-- Local Reviewer.app: drop a video on it (or open it and choose one) to review it in the
-- browser with frame-accurate notes. Built from this file by build_app.sh; it runs launch.py.

on run
	set f to choose file with prompt "Choose a video to review" of type {"public.movie"}
	reviewVideo(POSIX path of f)
end run

on open theFiles
	repeat with f in theFiles
		reviewVideo(POSIX path of f)
	end repeat
end open

on reviewVideo(p)
	set launcher to (POSIX path of (path to home folder)) & ".claude/skills/local-review/launch.py"
	set py to "/usr/bin/python3"
	repeat with c in {"/opt/homebrew/bin/python3", "/opt/homebrew/bin/python3.12", "/opt/homebrew/bin/python3.13", "/usr/local/bin/python3"}
		try
			do shell script "test -x " & quoted form of c
			set py to c
			exit repeat
		end try
	end repeat
	try
		do shell script quoted form of py & " " & quoted form of launcher & " " & quoted form of p
	on error msg
		display dialog "Local Reviewer couldn't open this video:" & return & return & msg buttons {"OK"} default button 1 with icon caution
	end try
end reviewVideo

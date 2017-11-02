#!/bin/zsh
exec $(dmenu_path_c | sort -u | \
    dmenu -fn 'xft:Terminus:pixelsize=12:autohint=true' \
    -nb '#000000' -nf '#FFFFFF' -sb '#1793d1' -b -i)

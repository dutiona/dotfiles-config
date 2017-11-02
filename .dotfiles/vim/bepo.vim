" {W} -> [É]
" ——————————
" On remappe W sur É :
noremap é w
noremap É W
" Corollaire, pour effacer/remplacer un mot quand on n’est pas au début (daé / laé).
" (attention, cela diminue la réactivité du {A}…)
noremap aé aw
noremap aÉ aW
" Pour faciliter les manipulations de fenêtres, on utilise {W} comme un Ctrl+W :
noremap w <C-w>
noremap W <C-w><C-w>

" [HJKL] -> {CTSR}
" ————————————————
" {cr} = « gauche / droite »
noremap c h
noremap r l
" {ts} = « haut / bas »
noremap t j
noremap s k
" {CR} = « haut / bas de l'écran »
noremap C H
noremap R L
" {TS} = « joindre / aide »
noremap T J
noremap S K
" Corollaire : repli suivant / précédent
noremap zs zj
noremap zt zk

" {HJKL} <- [CTSR]
" ————————————————
" {J} = « Jusqu'à »            (j = suivant, J = précédant)
noremap j t
noremap J T
" {L} = « Change »             (h = bloc, H = jusqu'à la fin de ligne)
noremap l c
noremap L C
" {H} = « Remplace »           (l = caractère, L = texte)
noremap h r
noremap H R
" {K} = « Substitue »          (k = caractère, K = ligne)
noremap k s
noremap K S
" Corollaire : correction orthographique
noremap ]k ]s
noremap [k [s

" Désambiguation de {g}
" —————————————————————
" ligne écran précédente / suivante (à l'intérieur d'une phrase)
noremap gs gk
noremap gt gj
" onglet précédant / suivant
noremap gb gT
noremap gé gt
"" optionnel : {gB} / {gÉ} pour aller au premier / dernier onglet
noremap gB :exe "silent! tabfirst"<CR>
noremap gÉ :exe "silent! tablast"<CR>
"" optionnel : {g"} pour aller au début de la ligne écran
"noremap g" g0

" <> en direct
" ————————————
nnoremap « <
nnoremap » >
vnoremap « <gv
vnoremap » >gv


"" Chiffres en accès direct
"" ————————————————————————
"noremap " 1
"noremap 1 "
"noremap « 2
"noremap 2 <
"noremap » 3
"noremap 3 >
"noremap ( 4
"noremap 4 (
"noremap ) 5
"noremap 5 )
"noremap @ 6
"noremap 6 @
"noremap + 7
"noremap 7 +
"noremap - 8
"noremap 8 -
"noremap / 9
"noremap 9 /
"noremap * 0
"noremap 0 *

"" Unite remapping
autocmd FileType unite call s:unite_settings()
function!  s:unite_settings()
    nmap <buffer> t <Plug>(unite_loop_cursor_down)
    nmap <buffer> s <Plug>(unite_loop_cursor_up)
    nmap <buffer> T <Plug>(unite_skip_cursor_down)
    nmap <buffer> S <Plug>(unite_skip_cursor_up)
    nmap <buffer><silent><expr> j unite#smart_map('j', unite#do_action('tabopen'))
endfunction

"" NERDTree remapping
let g:NERDTreeMapChdir = 'H'
let g:NERDTreeMapChdir = 'hd'
let g:NERDTreeMapCWD = 'HD'
let g:NERDTreeMapOpenInTab = 'j'
let g:NERDTreeMapOpenInTabSilent = 'J'
let g:NERDTreeMapJumpLastChild = 'T'
let g:NERDTreeMapOpenVSplit = 'v'
let g:NERDTreeMapRefresh = 'l'
let g:NERDTreeMapRefreshRoot = 'L'

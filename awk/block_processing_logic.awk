####################################################################
# A good example how to flag lines and process texts accordingly
# X. Jia Mar 27, 2019 @ New York
# https://stackoverflow.com/questions/55375083/awk-script-to-process-information-spread-over-multiple-file-lines/55389736
####################################################################
BEGIN{
    subs      = " xyz=1 "
    threshold = 3673
}

# function to append extra text to line
# and followed by comments if applicable
function get_extra_text(     extra_text) {    
    extra_text = sprintf("%s &\n%20s", prev, subs)
    text = (text ? text ORS : "") extra_text
    if (prev_is_comment) {
        text = text ORS comment
        prev_is_comment = 0
        comment = ""
    }
    return text
}

# return boolean if the current line is a new element
function is_new_element(){
    return ($1 ~ /^[0-9]+$/) && (($2 ~ /^[0-9]+$/ && $3~/\./) || ($2 == 0 && $3 !~ /\./))
}

# return boolean if current line is a comment or empty line
function is_comment() {
    return /^\s*[cC] / || /^\s*$/
}

NR < threshold {
# process from line-1 to the first EMPTY line
#NR==1,/^\s*$/ {
    # if the current line is a new element
    if (is_new_element()) {
        # save the last line and preceeding comments into the variable 'text'
        if (has_passed_first_block) text = get_extra_text()
	prev_is_new = 1
	has_passed_first_block = 1
    # before the first new element, all lines printed as-is
    } else if (!has_passed_first_block) {
        print 
        next
    # if current line is a comment
    } else if (is_comment()) {
        comment = (comment ? comment ORS : "") $0
        prev_is_comment = 1
        next
    # if the current line is neither new nor comment
    } else {
        # if previous line a new element
        if (prev_is_new) {
            print (text ? text ORS : "") prev
            text = ""
        # if previous line is comment
        } else if (prev_is_comment) {
            print prev ORS comment
            prev_is_comment = 0
            comment = ""
        } else {
            print prev
        }
        prev_is_new = 0
    }
    # prev saves the last non-comment line
    prev = $0
    next
}
# print the last block if NR > threshold 
!is_last_block_printed {
    print get_extra_text()
    is_last_block_printed = 1;
}

# print lines when NR > threshold or after the first EMPTY line
{   print "-" $0 }


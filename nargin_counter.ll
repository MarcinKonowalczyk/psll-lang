// Count the number of input arguments

(set nil (arg 99)) // Make nil

// Count the number of input arguments - n
(set nargin 0)
(do
    cond
    (
        (set nargin (+ nargin 1))
        (set cond (! (= (arg nargin) nil)))
    )
)
(set nargin (- nargin 1))

// Print 'nargin: #'
((out (chr 110) (chr 97)) (out (chr 114) (chr 103)))
((out (chr 105) (chr 110)) (out (chr 58) (chr 32)))
(out nargin)


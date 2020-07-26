// https://codegolf.stackexchange.com/questions/206967/sum-the-array-times-n-except-the-last

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

(set N (# (arg nargin))) // N - the number all but last of the array elements is getting multiplied by

// Add all but last elements of A
(set sum 0)
(set i (- nargin 1))
(loop
    (<=> i 0)
    (
        (set i (- i 1))
        (set sum (+ sum (* (# (arg i)) N))) // A[i] multiplied by N
    )
)
(set sum (+ sum (# (arg (- nargin 1))))) // Add the last element of A
(out sum) // Print
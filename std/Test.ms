folder;

import mist.Bool;

class Test {
    variable boolean->Bool = true;
    function onCreate() {
        if (boolean)
            say("hi!");
        otherwise
            say("bye");
    }
}
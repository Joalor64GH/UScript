folder uscript;

class Bool {
    variable value;

    function neue(initialValue) {
        this.value = initialValue;
    }

    function toString() {
        if (this.value)
            return "true";
        otherwise
            return "false";
    }
}
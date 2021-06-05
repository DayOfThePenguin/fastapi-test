import {
    createMuiTheme
} from '@material-ui/core/styles';

const theme = createMuiTheme({
    "palette": {
        "common": {
            "black": "#000",
            "white": "#fff"
        },
        "background": {
            "paper": "rgba(105, 140, 120, 1)",
            "default": "rgba(8, 12, 38, 1)"
        },
        "primary": {
            "light": "rgba(255, 255, 212, 1)",
            "main": "rgba(242, 222, 162, 1)",
            "dark": "rgba(190, 172, 115, 1)",
            "contrastText": "rgba(0, 0, 0, 1)"
        },
        "secondary": {
            "light": "rgba(255, 135, 92, 1)",
            "main": "rgba(242, 84, 48, 1)",
            "dark": "rgba(184, 26, 2, 1)",
            "contrastText": "rgba(0, 0, 0, 1)"
        },
        "error": {
            "light": "rgba(255, 87, 60, 1)",
            "main": "rgba(242, 1, 14, 1)",
            "dark": "rgba(182, 0, 0, 1)",
            "contrastText": "rgba(0, 0, 0, 1)"
        },
        "text": {
            "primary": "rgba(255, 255, 255, 1)",
            "secondary": "rgba(242, 222, 162, 1)",
            "disabled": "rgba(208, 2, 27, 1)",
            "hint": "rgba(0, 0, 0, 0.38)"
        }
    }
});
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import CircularProgress from '@material-ui/core/CircularProgress';


let LoadingAlert = () => {
    return (
        <Alert iconMapping={{ loading: <CircularProgress fontSize="inherit" /> }} severity="loading">
            This is a loading alert — check it out!
        </Alert>
    );
}

export default LoadingAlert;
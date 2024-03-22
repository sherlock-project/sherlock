import { CssVarsProvider  } from '@mui/joy/styles';

import '../node_modules/reset-css/reset.css';
import { Sheet, Typography } from '@mui/joy';
import Form from './components/form';

const mainSheetStyle = {
  width: "100%", 
  height: "100%",
  padding: "10px",
  boxSizing: "border-box",
  overflow: "hidden"
};

export default function Home() {
  return (
    <CssVarsProvider defaultMode="dark" modeStorageKey="theme">
      <Sheet sx={mainSheetStyle}>
        <Typography level="h1" textAlign="center">
            Sherlock
        </Typography>

        <Form />
      </Sheet>
    </CssVarsProvider>
  );
}

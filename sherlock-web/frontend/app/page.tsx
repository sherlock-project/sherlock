"use client"
import { CssVarsProvider  } from '@mui/joy/styles';

import '../node_modules/reset-css/reset.css';
import { Box, Button, Grid, Link, Sheet, Stack, Typography } from '@mui/joy';
import Form from './components/form';
import { useState } from 'react';

const mainSheetStyle = {
  width: "100vw", 
  height: "100vh",
  padding: "10px",
  boxSizing: "border-box",
  overflow: "hidden"
};

export type pageList = {
  name: string,
  url: string
}[];

export default function Home() {
  const [foundData, setFoundData] = useState<pageList | null>(null);
  
  return (
    <CssVarsProvider defaultMode="dark" modeStorageKey="theme">
      <Sheet sx={mainSheetStyle}>
        <Typography level="h1" textAlign="center">
            Sherlock
        </Typography>

        {foundData ? 
          <Stack direction="column" spacing={2} sx={{height: "95%"}}>
            <Typography level="h4" textAlign="center">Found sites:</Typography>
          
            <Grid container spacing={2}  columns={{ xs: 4, sm: 6, md: 8, lg: 10, xl: 12 }} sx={{height: "95%", overflow: "auto"}}>
              {foundData.map(({name, url}) => {
                  return (
                      <Grid xs={2} key={"found-"+name}>
                          <Link href={url} target="_blank" rel="noreferrer" textAlign="center" sx={{width: "100%", display: "block"}}>
                              {name}
                          </Link>
                      </Grid>
                  )
              })}
            </Grid>

            <Button color="neutral" onClick={() => setFoundData(null)}>Back</Button>
          </Stack>
          : <Form setFoundData={setFoundData} /> }
      </Sheet>
    </CssVarsProvider>
  );
}

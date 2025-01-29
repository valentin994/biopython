"""Toolset for accessing alphahold database for bulk downloads and possibly more"""

import argparse
import asyncio
from pprint import pprint
from ftplib import FTP
from platformdirs import user_downloads_dir

import httpx

# TODO implement with aioftp so everything is async


class AFDB:
    """
    Toolset for working with the alphafold database.
    """

    def __init__(
        self,
        ftp_server: str = "ftp.ebi.ac.uk",
        download_directory: str = user_downloads_dir(),
        version: str = "latest",
    ) -> None:
        """TODO"""
        self.ftp_server = ftp_server
        self.download_directory = download_directory
        self.version = version
        self.api_client = httpx.AsyncClient()

    async def get_readme(self) -> str:
        """
        Read the README.txt file.

        :return Parsed README.txt file, or in a a case of an exception, return an error message
        :rtype str
        """
        try:
            request_readme = await self.api_client.get(
                f"https://{self.ftp_server}/pub/databases/alphafold/README.txt"
            )
            request_readme.raise_for_status()
            await self.api_client.aclose()
        except httpx.HTTPStatusError as err:
            return f"Exception occured for fetching the README. {err}"
        except httpx.RequestError as err:
            return f"Error occurred during the request: {err}"
        return request_readme.text

    async def get_metadata_json(self) -> dict | str:
        """
        Read the download_metadata.json file.

        :return Parsed download_metadata.json file, or in case of an exception, return an error message
        :rtype dict | str
        """
        try:
            request_metadata = await self.api_client.get(
                f"https://{self.ftp_server}/pub/databases/alphafold/download_metadata.json"
            )
            request_metadata.raise_for_status()
            await self.api_client.aclose()
        except httpx.HTTPStatusError as err:
            return f"Exception occured for fetching the README. {err}"
        except httpx.RequestError as err:
            return f"Error occurred during the request: {err}"
        return request_metadata.json()

    def list_accessions(self) -> list[str]:
        """
        List all accession in the alphafold latets directory.

        :return List of file names
        :rtype list[str]
        """
        directories = []
        with FTP("ftp.ebi.ac.uk") as ftp:
            ftp.login()
            ftp.cwd(f"/pub/databases/alphafold/{self.version}/")
            directories = ftp.nlst()
        return directories

    def download_accession_by_reference_proteom(self, reference_proteom) -> str:
        """
        Download a tar archive from the ftp server based on the uniprot ID provided.

        :param reference_proteom: Alphafold identifier #TODO better description
        :type reference_proteom: str
        :return: A message where and what file has been downloaded.
        :rtype: str
        """
        download_file = ""
        with FTP("ftp.ebi.ac.uk") as ftp:
            ftp.login()
            ftp.cwd(f"/pub/databases/alphafold/{self.version}/")
            for accession in ftp.nlst():
                if accession.split("_")[0] == reference_proteom:
                    download_file = accession
                    break
            with open(
                f"{self.download_directory}/{download_file}", "wb"
            ) as file_handler:
                ftp.retrbinary(f"RETR {download_file}", file_handler.write)
        return f"Downloaded {download_file} into {self.download_directory}"


async def main():
    """Main handler for running the helper"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="Get the metadata from alphafold, the list contains all the archive files available for bulk download.",
    )
    parser.add_argument(
        "-r",
        "--readme",
        action="store_true",
        help="Get the readme from alphahold ftp server",
    )
    parser.add_argument(
        "-ls",
        "--list_acs",
        action="store_true",
        help="List accessions from the ftp server",
    )
    parser.add_argument(
        "-da",
        "--download_accession",
        help="Download an accession by providing the reference proteom id",
    )
    # TODO add a way to setup version
    afdb = AFDB()
    args = parser.parse_args()
    if args.metadata:
        pprint(await afdb.get_metadata_json())
    elif args.readme:
        print(await afdb.get_readme())
    elif args.list_acs:
        for accession in afdb.list_accessions():
            if accession.startswith("UP"):
                print(accession)
    elif args.download_accession:
        print(afdb.download_accession_by_reference_proteom(args.download_accession))


if __name__ == "__main__":
    asyncio.run(main())
